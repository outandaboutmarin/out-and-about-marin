// save-profile — open item 24 (users-table lockdown).
// Updates a whitelisted set of profile columns after proving the caller owns the
// account. Accepts EITHER the 4-digit `pin` OR `pin_hash` (the SHA-256 hex the
// browser keeps after sign-in). The browser has always stored the hash, not the
// digits, so a pin-only version of this function would reject every save from
// an already-signed-in visitor.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

// Never pin, phone, id or member_since.
const ALLOWED = ["name", "zip", "ages", "referral", "saved_events", "default_filters"];

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const { phone, pin, pin_hash, updates } = await req.json();
    const digits = String(phone || "").replace(/\D/g, "");
    let hash = "";
    if (/^\d{4}$/.test(String(pin || ""))) hash = await sha256Hex(String(pin));
    else if (/^[0-9a-f]{64}$/.test(String(pin_hash || ""))) hash = String(pin_hash);
    if (digits.length !== 10 || !hash) return json({ ok: false, code: "invalid" });

    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const { data: owner } = await supabase.from("users").select("phone").eq("phone", digits).eq("pin", hash).maybeSingle();
    if (!owner) return json({ ok: false, code: "unauthorized" });

    const clean: Record<string, unknown> = {};
    for (const k of ALLOWED) if (updates && k in updates) clean[k] = updates[k];
    if (Object.keys(clean).length === 0) return json({ ok: true });

    const { error } = await supabase.from("users").update(clean).eq("phone", digits);
    if (error) { console.error(error); return json({ ok: false, code: "server" }, 500); }
    return json({ ok: true });
  } catch (e) { console.error(e); return json({ ok: false, code: "server" }, 500); }
});

async function sha256Hex(s: string) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}
function json(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { ...cors, "Content-Type": "application/json" } });
}
