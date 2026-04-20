import random
import streamlit.components.v1 as components

MOTIVATIONAL_IMAGES = [
    "https://images.unsplash.com/photo-1558611848-73f7eb4001a1",
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
    "https://images.unsplash.com/photo-1599058917212-d750089bc07e",
    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
]
 
 
def display_genai_advice(timestamp, content, image):
    """Displays AI-generated workout advice as a rich, styled HTML card.
 
    Features a dark athletic aesthetic with a hero image, animated glowing
    badge, bold typography, and a formatted timestamp footer.
 
    If no image is provided (or it is falsy), a random image is selected
    from the built-in MOTIVATIONAL_IMAGES pool on each call.
 
    Args:
        timestamp: A datetime object representing when the advice was generated.
        content: The text content of the AI advice.
        image: A URL string for the hero image, or None.
    """
    formatted_time = timestamp.strftime("%B %d, %Y  ·  %I:%M %p")
    resolved_image = random.choice(MOTIVATIONAL_IMAGES)
 
    image_section = ""
    if resolved_image:
        image_section = f"""
        <div class="hero-image-wrapper">
            <img src="{resolved_image}" alt="Workout motivation" class="hero-image" />
            <div class="hero-overlay"></div>
        </div>
        """
 
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
 
    body {{
      background: transparent;
      padding: 8px 0 12px 0;
    }}
 
    .advice-card {{
      background: #0d0d0d;
      border-radius: 16px;
      overflow: hidden;
      max-width: 680px;
      margin: 0 auto;
      font-family: 'DM Sans', sans-serif;
      box-shadow:
        0 0 0 1px rgba(255,255,255,0.06),
        0 24px 60px rgba(0,0,0,0.6);
      animation: adviceFadeUp 0.5s cubic-bezier(.22,.68,0,1.2) both;
    }}
 
    @keyframes adviceFadeUp {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
 
    /* Hero image */
    .hero-image-wrapper {{
      position: relative;
      width: 100%;
      height: 260px;
      overflow: hidden;
    }}
    .hero-image {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transform: scale(1.05);
      transition: transform 7s ease;
    }}
    .advice-card:hover .hero-image {{
      transform: scale(1.0);
    }}
    .hero-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(
        to bottom,
        rgba(13,13,13,0.0)  0%,
        rgba(13,13,13,0.6) 70%,
        rgba(13,13,13,1.0) 100%
      );
    }}
 
    /* Card body */
    .advice-body {{
      padding: 26px 30px 30px;
    }}
 
    /* AI badge */
    .ai-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(250, 17, 79, 0.10);
      border: 1px solid rgba(250, 17, 79, 0.30);
      border-radius: 999px;
      padding: 5px 15px 5px 11px;
      margin-bottom: 20px;
    }}
    .ai-badge-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #fa114f;
      box-shadow: 0 0 8px 2px rgba(250,17,79,0.55);
      animation: badgePulse 2s ease-in-out infinite;
      flex-shrink: 0;
    }}
    @keyframes badgePulse {{
      0%, 100% {{ box-shadow: 0 0 8px 2px rgba(250,17,79,0.55); }}
      50%       {{ box-shadow: 0 0 3px 1px rgba(250,17,79,0.20); }}
    }}
    .ai-badge-label {{
      font-size: 0.70em;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #fa114f;
    }}
 
    /* Heading */
    .advice-heading {{
      font-family: 'Bebas Neue', sans-serif;
      font-size: 2.2em;
      letter-spacing: 0.06em;
      color: #ffffff;
      margin: 0 0 14px 0;
      line-height: 1.05;
    }}
 
    /* Red accent bar */
    .advice-divider {{
      width: 44px;
      height: 3px;
      background: linear-gradient(90deg, #fa114f, #ff6b35);
      border-radius: 2px;
      margin-bottom: 20px;
    }}
 
    /* Content text */
    .advice-content {{
      color: #bcbcbc;
      font-size: 0.97em;
      line-height: 1.80;
      margin: 0 0 26px 0;
      font-style: italic;
    }}
 
    /* Footer */
    .advice-footer {{
      display: flex;
      align-items: center;
      gap: 9px;
      border-top: 1px solid rgba(255,255,255,0.07);
      padding-top: 16px;
      color: #484848;
      font-size: 0.76em;
      letter-spacing: 0.04em;
    }}
    .advice-footer-icon {{
      font-size: 0.9em;
      opacity: 0.7;
    }}
  </style>
</head>
<body>
  <div class="advice-card">
    {image_section}
    <div class="advice-body">
 
      <div class="ai-badge">
        <span class="ai-badge-dot"></span>
        <span class="ai-badge-label">AI Trainer</span>
      </div>
 
      <h2 class="advice-heading">Your Workout Motivation</h2>
      <div class="advice-divider"></div>
 
      <p class="advice-content">{content}</p>
 
      <div class="advice-footer">
        <span class="advice-footer-icon">&#128336;</span>
        <span>Generated on {formatted_time}</span>
      </div>
 
    </div>
  </div>
</body>
</html>"""
 
    components.html(html, height=560)