// signup — open item 24 (users-table lockdown).
// Creates an account with the service role. Rejects a phone that already exists
// (this replaces the browser's old direct "does this phone exist?" read, which the
// lockdown makes impossible). Returns { ok:false, code:"exists" } with HTTP 200 so
// the client can tell the person to sign in instead.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const PROFILE = "id, phone, name, zip, ages, referral, saved_events, default_filters, plan, member_since";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const b = await req.json();
    const digits = String(b.phone || "").replace(/\D/g, "");
    if (digits.length !== 10 || !/^\d{4}$/.test(String(b.pin || "")))
      return json({ ok: false, code: "invalid" });

    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const { data: existing } = await supabase.from("users").select("phone").eq("phone", digits).maybeSingle();
    if (existing) return json({ ok: false, code: "exists" });

    const row = {
      phone: digits,
      pin: await sha256Hex(String(b.pin)),
      name: String(b.name || "").slice(0, 100),
      zip: String(b.zip || "").slice(0, 10),
      ages: Array.isArray(b.ages) ? b.ages : [],
      referral: String(b.referral || "").slice(0, 100),
      saved_events: Array.isArray(b.saved_events) ? b.saved_events : [],
      default_filters: b.default_filters && typeof b.default_filters === "object" ? b.default_filters : {},
      plan: "beta",
      member_since: b.member_since || new Date().toISOString().slice(0, 10),
    };
    const { data: user, error } = await supabase.from("users").insert([row]).select(PROFILE).single();
    if (error) {
      // A race between the existence check and the insert lands here as a unique violation.
      if ((error as { code?: string }).code === "23505") return json({ ok: false, code: "exists" });
      console.error(error); return json({ ok: false, code: "server" }, 500);
    }
    return json({ ok: true, user });
  } catch (e) { console.error(e); return json({ ok: false, code: "server" }, 500); }
});

async function sha256Hex(s: string) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}
function json(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { ...cors, "Content-Type": "application/json" } });
}
