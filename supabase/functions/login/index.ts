// login — open item 24 (users-table lockdown).
// Verifies phone + 4-digit PIN with the service role and returns the profile.
// The pin column is never sent to the browser; the browser keeps its own hash.
// Expected outcomes return HTTP 200 with { ok, code } so the client can read them
// through supabase.functions.invoke (which hides the body of non-2xx responses).
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
    const { phone, pin } = await req.json();
    const digits = String(phone || "").replace(/\D/g, "");
    if (digits.length !== 10 || !/^\d{4}$/.test(String(pin || "")))
      return json({ ok: false, code: "invalid" });

    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const { data: user, error } = await supabase
      .from("users").select(PROFILE)
      .eq("phone", digits).eq("pin", await sha256Hex(String(pin)))
      .maybeSingle();
    if (error) { console.error(error); return json({ ok: false, code: "server" }, 500); }
    if (!user) return json({ ok: false, code: "wrong" });
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
