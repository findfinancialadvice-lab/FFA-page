// Cloudflare Pages Function — POST /api/subscribe
// Adds an email to Brevo list 2 (single opt-in).
// The Brevo API key is read from env.BREVO_API_KEY (a Pages environment secret)
// and is never exposed to the client.

const BREVO_LIST_ID = 2;

const json = (body, status) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

// Basic, permissive email sanity check (real validation happens at Brevo).
const looksLikeEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

export async function onRequestPost(context) {
  const { request, env } = context;

  // Extract the email from a JSON body or a form-encoded body.
  let email = "";
  const contentType = request.headers.get("content-type") || "";
  try {
    if (contentType.includes("application/json")) {
      const data = await request.json();
      email = ((data && data.email) || "").toString().trim();
    } else {
      const form = await request.formData();
      email = (form.get("email") || "").toString().trim();
    }
  } catch (err) {
    return json({ success: false, error: "Invalid request body." }, 400);
  }

  if (!email || !looksLikeEmail(email)) {
    return json({ success: false, error: "Please enter a valid email address." }, 400);
  }

  if (!env.BREVO_API_KEY) {
    // Misconfiguration — the Pages secret hasn't been set.
    return json({ success: false, error: "Server not configured." }, 500);
  }

  let brevoRes;
  try {
    brevoRes = await fetch("https://api.brevo.com/v3/contacts", {
      method: "POST",
      headers: {
        "api-key": env.BREVO_API_KEY,
        "content-type": "application/json",
        accept: "application/json",
      },
      body: JSON.stringify({
        email,
        listIds: [BREVO_LIST_ID],
        updateEnabled: true,
      }),
    });
  } catch (err) {
    return json(
      { success: false, error: "Could not reach the mail service. Please try again." },
      502
    );
  }

  // 201 (created) or 204 (updated, e.g. existing contact) — both are success.
  if (brevoRes.ok) {
    return json({ success: true }, 200);
  }

  // An already-existing contact may still surface as a duplicate error —
  // they're on list 2 either way, so treat it as success.
  let errBody = {};
  try {
    errBody = await brevoRes.json();
  } catch (err) {
    // non-JSON error body — ignore
  }
  if (errBody && errBody.code === "duplicate_parameter") {
    return json({ success: true }, 200);
  }

  return json({ success: false, error: "Subscription failed. Please try again." }, 502);
}
