from flask import Flask, request, jsonify, send_file, render_template_string
import subprocess
import json
import os
import tempfile
import anthropic

app = Flask(__name__)

os.environ["ANTHROPIC_API_KEY"] = "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"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>SnapLogic Pitch Deck Generator</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: linear-gradient(135deg, #0a0f2e 0%, #0d2352 50%, #0a1a3e 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }

    .container {
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 20px;
      padding: 48px;
      width: 100%;
      max-width: 780px;
      box-shadow: 0 32px 80px rgba(0,0,0,0.5);
    }

    .logo-area {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 36px;
    }

    .logo-icon {
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, #00d4ff, #0077ff);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      font-weight: 900;
      color: white;
      flex-shrink: 0;
    }

    .logo-text h1 {
      font-size: 22px;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.3px;
    }

    .logo-text p {
      font-size: 13px;
      color: rgba(255,255,255,0.5);
      margin-top: 2px;
    }

    label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: rgba(255,255,255,0.7);
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    textarea {
      width: 100%;
      padding: 16px 18px;
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 12px;
      color: #ffffff;
      font-size: 14.5px;
      font-family: inherit;
      line-height: 1.6;
      resize: vertical;
      transition: all 0.2s;
      outline: none;
    }

    textarea::placeholder { color: rgba(255,255,255,0.3); }
    textarea:focus { border-color: #00d4ff; background: rgba(255,255,255,0.1); box-shadow: 0 0 0 3px rgba(0,212,255,0.1); }

    .field { margin-bottom: 22px; }

    .divider {
      height: 1px;
      background: rgba(255,255,255,0.08);
      margin: 28px 0;
    }

    .options-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 28px;
    }

    .option-card {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 10px;
      padding: 14px 16px;
    }

    select {
      width: 100%;
      background: transparent;
      border: none;
      color: #ffffff;
      font-size: 14px;
      font-family: inherit;
      outline: none;
      cursor: pointer;
      margin-top: 6px;
    }

    select option { background: #0d2352; color: white; }

    .btn {
      width: 100%;
      padding: 16px;
      background: linear-gradient(135deg, #00d4ff 0%, #0077ff 100%);
      border: none;
      border-radius: 12px;
      color: white;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      letter-spacing: 0.3px;
      transition: all 0.2s;
      position: relative;
    }

    .btn:hover { transform: translateY(-1px); box-shadow: 0 12px 32px rgba(0,119,255,0.4); }
    .btn:active { transform: translateY(0); }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

    .status {
      margin-top: 22px;
      padding: 16px 20px;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 500;
      display: none;
      align-items: center;
      gap: 12px;
    }

    .status.loading {
      display: flex;
      background: rgba(0,119,255,0.15);
      border: 1px solid rgba(0,119,255,0.3);
      color: #80c8ff;
    }

    .status.success {
      display: flex;
      background: rgba(0,200,100,0.15);
      border: 1px solid rgba(0,200,100,0.3);
      color: #80ffb8;
    }

    .status.error {
      display: flex;
      background: rgba(255,80,80,0.15);
      border: 1px solid rgba(255,80,80,0.3);
      color: #ffaaaa;
    }

    .spinner {
      width: 18px; height: 18px;
      border: 2px solid rgba(255,255,255,0.2);
      border-top-color: #00d4ff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      flex-shrink: 0;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .download-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-top: 14px;
      padding: 12px 24px;
      background: linear-gradient(135deg, #00c864, #00a850);
      border-radius: 10px;
      color: white;
      font-weight: 700;
      font-size: 14px;
      text-decoration: none;
      transition: all 0.2s;
    }

    .download-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(0,200,100,0.4); }

    .badge {
      display: inline-block;
      padding: 3px 10px;
      background: rgba(0,212,255,0.15);
      border: 1px solid rgba(0,212,255,0.3);
      border-radius: 20px;
      font-size: 11px;
      color: #00d4ff;
      font-weight: 600;
      letter-spacing: 0.5px;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
<div class="container">
  <div class="logo-area">
    <div class="logo-icon">SL</div>
    <div class="logo-text">
      <h1>SnapLogic Pitch Deck Generator</h1>
      <p>AI-powered customer presentations in seconds</p>
    </div>
  </div>

  <span class="badge">✦ Powered by Claude AI</span>

  <div class="field">
    <label>About the Customer</label>
    <textarea id="customer" rows="5" placeholder="e.g. Acme Corp is a Fortune 500 retail company with 200+ locations. They struggle with siloed data across SAP, Salesforce, and legacy ERPs. Their IT team of 40 spends most time on manual integrations..."></textarea>
  </div>

  <div class="field">
    <label>How SnapLogic Can Help</label>
    <textarea id="snaplogic" rows="5" placeholder="e.g. SnapLogic can unify their data pipelines with pre-built Snaps for SAP and Salesforce, reduce integration time by 80%, enable real-time inventory visibility, and empower citizen integrators with the low-code designer..."></textarea>
  </div>

  <div class="divider"></div>

  <div class="options-row">
    <div class="option-card">
      <label>Slide Count</label>
      <select id="slideCount">
        <option value="6">6 Slides (Quick)</option>
        <option value="8" selected>8 Slides (Standard)</option>
        <option value="10">10 Slides (Full)</option>
      </select>
    </div>
    <div class="option-card">
      <label>Tone</label>
      <select id="tone">
        <option value="executive">Executive</option>
        <option value="technical">Technical</option>
        <option value="consultative" selected>Consultative</option>
      </select>
    </div>
  </div>

  <button class="btn" onclick="generateDeck()" id="genBtn">
    ✦ Generate Pitch Deck
  </button>

  <div class="status loading" id="statusLoading">
    <div class="spinner"></div>
    <span id="statusText">Generating your deck with AI...</span>
  </div>

  <div class="status success" id="statusSuccess">
    <span>✓</span>
    <div>
      <div>Your pitch deck is ready!</div>
      <a class="download-btn" id="downloadLink" href="#" download>
        ⬇ Download PPTX
      </a>
    </div>
  </div>

  <div class="status error" id="statusError">
    <span>✕</span>
    <span id="errorText">Something went wrong. Please try again.</span>
  </div>
</div>

<script>
async function generateDeck() {
  const customer = document.getElementById('customer').value.trim();
  const snaplogic = document.getElementById('snaplogic').value.trim();
  const slideCount = document.getElementById('slideCount').value;
  const tone = document.getElementById('tone').value;

  if (!customer || !snaplogic) {
    alert('Please fill in both fields.');
    return;
  }

  const btn = document.getElementById('genBtn');
  btn.disabled = true;
  btn.textContent = 'Generating...';

  document.getElementById('statusLoading').style.display = 'flex';
  document.getElementById('statusSuccess').style.display = 'none';
  document.getElementById('statusError').style.display = 'none';

  const steps = [
    'Analyzing customer context...',
    'Crafting slide structure...',
    'Generating visual content...',
    'Building your PPTX...'
  ];
  let step = 0;
  const statusText = document.getElementById('statusText');
  const interval = setInterval(() => {
    step = (step + 1) % steps.length;
    statusText.textContent = steps[step];
  }, 3000);

  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer, snaplogic, slideCount: parseInt(slideCount), tone })
    });

    clearInterval(interval);

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.error || 'Server error');
    }

    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    document.getElementById('downloadLink').href = url;
    document.getElementById('downloadLink').download = 'SnapLogic_Pitch_Deck.pptx';

    document.getElementById('statusLoading').style.display = 'none';
    document.getElementById('statusSuccess').style.display = 'flex';
  } catch (e) {
    clearInterval(interval);
    document.getElementById('statusLoading').style.display = 'none';
    document.getElementById('statusError').style.display = 'flex';
    document.getElementById('errorText').textContent = e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = '✦ Generate Pitch Deck';
  }
}
</script>
</body>
</html>
"""

SLIDE_GEN_PROMPT = """You are a SnapLogic sales expert creating a professional pitch deck.

Customer Info:
{customer}

How SnapLogic Can Help:
{snaplogic}

Create {slide_count} slides for a {tone} pitch deck. Output ONLY valid JSON (no markdown, no explanation).

Return this exact structure:
{{
  "company_name": "extracted or inferred company name",
  "slides": [
    {{
      "type": "title",
      "title": "slide title",
      "subtitle": "subtitle text",
      "presenter_notes": "brief speaker note"
    }},
    {{
      "type": "challenge",
      "title": "slide title",
      "points": ["challenge 1", "challenge 2", "challenge 3"],
      "stat": "impactful statistic or insight",
      "presenter_notes": "brief speaker note"
    }},
    {{
      "type": "solution",
      "title": "slide title", 
      "points": ["solution 1", "solution 2", "solution 3", "solution 4"],
      "presenter_notes": "brief speaker note"
    }},
    {{
      "type": "value",
      "title": "slide title",
      "metrics": [
        {{"label": "metric name", "value": "X%", "description": "what it means"}},
        {{"label": "metric name", "value": "Xh", "description": "what it means"}},
        {{"label": "metric name", "value": "Xx", "description": "what it means"}}
      ],
      "presenter_notes": "brief speaker note"
    }},
    {{
      "type": "capabilities",
      "title": "slide title",
      "items": [
        {{"icon": "🔗", "title": "capability", "desc": "short description"}},
        {{"icon": "⚡", "title": "capability", "desc": "short description"}},
        {{"icon": "🔒", "title": "capability", "desc": "short description"}},
        {{"icon": "📊", "title": "capability", "desc": "short description"}}
      ],
      "presenter_notes": "brief speaker note"
    }},
    {{
      "type": "use_cases",
      "title": "slide title",
      "use_cases": [
        {{"title": "use case 1", "desc": "description"}},
        {{"title": "use case 2", "desc": "description"}},
        {{"title": "use case 3", "desc": "description"}}
      ],
      "presenter_notes": "brief speaker note"
    }},
    {{
      "type": "why_snaplogic",
      "title": "Why SnapLogic",
      "reasons": ["reason 1", "reason 2", "reason 3", "reason 4"],
      "tagline": "compelling one-liner",
      "presenter_notes": "brief speaker note"
    }},
    {{
      "type": "next_steps",
      "title": "Next Steps",
      "steps": [
        {{"num": "01", "action": "action title", "desc": "description"}},
        {{"num": "02", "action": "action title", "desc": "description"}},
        {{"num": "03", "action": "action title", "desc": "description"}}
      ],
      "cta": "call to action text",
      "presenter_notes": "brief speaker note"
    }}
  ]
}}

Make ALL content specific to this customer's industry and needs. Be concrete and compelling.
For slide_count < 8, merge or drop less critical slides. Always keep title, solution, value, and next_steps.
"""

PPTX_TEMPLATE = """
const pptxgen = require('pptxgenjs');
const fs = require('fs');

const data = {data};

async function buildDeck() {{
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.title = 'SnapLogic - ' + data.company_name;

  // Color palette - Ocean Executive
  const C = {{
    navy:    '0A1628',
    blue:    '0A4FA8',
    cyan:    '00D4FF',
    white:   'FFFFFF',
    offWhite:'F0F4FF',
    lightBg: 'EBF2FF',
    muted:   '8BA3C7',
    dark:    '061020',
    accent:  '00D4FF',
    green:   '00C864',
  }};

  function makeShadow() {{
    return {{ type: 'outer', color: '000000', opacity: 0.18, blur: 8, offset: 3, angle: 135 }};
  }}

  for (const slide_data of data.slides) {{
    const slide = pres.addSlide();

    if (slide_data.type === 'title') {{
      // Full dark background
      slide.background = {{ color: C.navy }};

      // Left accent bar
      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 0.35, h: 5.625,
        fill: {{ color: C.cyan }}, line: {{ type: 'none' }}
      }});

      // Right decorative block
      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 6.5, y: 0, w: 3.5, h: 5.625,
        fill: {{ color: '061630' }}, line: {{ type: 'none' }}
      }});

      // Geometric accent
      slide.addShape(pres.shapes.OVAL, {{
        x: 7.5, y: 1.0, w: 2.2, h: 2.2,
        fill: {{ color: C.cyan, transparency: 85 }},
        line: {{ color: C.cyan, width: 1.5, transparency: 60 }}
      }});
      slide.addShape(pres.shapes.OVAL, {{
        x: 8.0, y: 2.5, w: 1.4, h: 1.4,
        fill: {{ color: C.blue, transparency: 70 }},
        line: {{ type: 'none' }}
      }});

      // SnapLogic label
      slide.addText('SNAPLOGIC', {{
        x: 0.6, y: 0.4, w: 5.5, h: 0.35,
        fontSize: 11, color: C.cyan, bold: true, charSpacing: 4,
        margin: 0
      }});

      // Main title
      slide.addText(slide_data.title, {{
        x: 0.6, y: 1.0, w: 5.6, h: 2.0,
        fontSize: 38, color: C.white, bold: true,
        wrap: true, valign: 'top', margin: 0
      }});

      // Subtitle
      slide.addText(slide_data.subtitle || '', {{
        x: 0.6, y: 3.2, w: 5.6, h: 0.9,
        fontSize: 15, color: C.muted, wrap: true, margin: 0
      }});

      // Bottom bar
      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0.35, y: 5.1, w: 6.15, h: 0.05,
        fill: {{ color: C.blue }}, line: {{ type: 'none' }}
      }});
      slide.addText('Intelligent Integration Platform', {{
        x: 0.6, y: 5.15, w: 5.5, h: 0.3,
        fontSize: 10, color: C.muted, margin: 0
      }});

    }} else if (slide_data.type === 'challenge') {{
      slide.background = {{ color: C.white }};

      // Top bar
      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 10, h: 0.9,
        fill: {{ color: C.navy }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.title, {{
        x: 0.4, y: 0.12, w: 7, h: 0.65,
        fontSize: 22, color: C.white, bold: true, margin: 0, valign: 'middle'
      }});
      slide.addText('CHALLENGE', {{
        x: 7.5, y: 0.25, w: 2.1, h: 0.4,
        fontSize: 9, color: C.cyan, bold: true, charSpacing: 3,
        align: 'right', margin: 0
      }});

      // Left: pain points
      const points = (slide_data.points || []).slice(0, 4);
      points.forEach((pt, i) => {{
        const yPos = 1.1 + i * 0.9;
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: 0.4, y: yPos, w: 4.8, h: 0.72,
          fill: {{ color: C.lightBg }}, line: {{ color: C.blue, width: 0.5 }},
          shadow: makeShadow()
        }});
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: 0.4, y: yPos, w: 0.06, h: 0.72,
          fill: {{ color: C.cyan }}, line: {{ type: 'none' }}
        }});
        slide.addText(pt, {{
          x: 0.62, y: yPos, w: 4.4, h: 0.72,
          fontSize: 13, color: C.navy, wrap: true, valign: 'middle', margin: 6
        }});
      }});

      // Right: stat card
      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 5.7, y: 1.1, w: 3.9, h: 4.1,
        fill: {{ color: C.navy }}, line: {{ type: 'none' }},
        shadow: makeShadow()
      }});
      slide.addShape(pres.shapes.OVAL, {{
        x: 6.5, y: 1.4, w: 1.8, h: 1.8,
        fill: {{ color: C.cyan, transparency: 88 }},
        line: {{ color: C.cyan, width: 1, transparency: 50 }}
      }});
      slide.addText('KEY INSIGHT', {{
        x: 5.9, y: 1.25, w: 3.5, h: 0.3,
        fontSize: 9, color: C.cyan, bold: true, charSpacing: 2, align: 'center', margin: 0
      }});
      slide.addText(slide_data.stat || '', {{
        x: 5.9, y: 1.7, w: 3.5, h: 3.2,
        fontSize: 14.5, color: C.white, align: 'center', valign: 'middle', wrap: true, margin: 10
      }});

    }} else if (slide_data.type === 'solution') {{
      slide.background = {{ color: C.offWhite }};

      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 10, h: 0.9,
        fill: {{ color: C.blue }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.title, {{
        x: 0.4, y: 0.12, w: 8, h: 0.65,
        fontSize: 22, color: C.white, bold: true, margin: 0, valign: 'middle'
      }});
      slide.addText('SOLUTION', {{
        x: 8.0, y: 0.25, w: 1.7, h: 0.4,
        fontSize: 9, color: C.cyan, bold: true, charSpacing: 3, align: 'right', margin: 0
      }});

      // 2x2 grid
      const pts = (slide_data.points || []).slice(0, 4);
      const grid = [
        {{ x: 0.4, y: 1.1 }}, {{ x: 5.2, y: 1.1 }},
        {{ x: 0.4, y: 3.2 }}, {{ x: 5.2, y: 3.2 }}
      ];
      const icons = ['🔗','⚡','🛡️','📊'];
      pts.forEach((pt, i) => {{
        const g = grid[i];
        if (!g) return;
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: g.x, y: g.y, w: 4.5, h: 1.8,
          fill: {{ color: C.white }}, line: {{ color: '00000010' }},
          shadow: makeShadow()
        }});
        slide.addText(icons[i] || '✓', {{
          x: g.x + 0.15, y: g.y + 0.15, w: 0.55, h: 0.55,
          fontSize: 18, align: 'center', margin: 0
        }});
        slide.addText(pt, {{
          x: g.x + 0.2, y: g.y + 0.75, w: 4.1, h: 0.95,
          fontSize: 12.5, color: C.navy, wrap: true, valign: 'top', margin: 4
        }});
      }});

    }} else if (slide_data.type === 'value') {{
      slide.background = {{ color: C.navy }};

      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 0.25, h: 5.625,
        fill: {{ color: C.cyan }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.title, {{
        x: 0.5, y: 0.25, w: 9, h: 0.6,
        fontSize: 26, color: C.white, bold: true, margin: 0
      }});
      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0.5, y: 0.88, w: 9, h: 0.03,
        fill: {{ color: C.blue }}, line: {{ type: 'none' }}
      }});

      const metrics = (slide_data.metrics || []).slice(0, 3);
      const spacing = 3.0;
      metrics.forEach((m, i) => {{
        const xPos = 0.5 + i * spacing;
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: xPos, y: 1.1, w: 2.7, h: 3.8,
          fill: {{ color: '0D2040' }}, line: {{ color: C.blue, width: 0.5 }},
          shadow: makeShadow()
        }});
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: xPos, y: 1.1, w: 2.7, h: 0.06,
          fill: {{ color: C.cyan }}, line: {{ type: 'none' }}
        }});
        slide.addText(m.value || '', {{
          x: xPos, y: 1.4, w: 2.7, h: 1.2,
          fontSize: 44, color: C.cyan, bold: true, align: 'center', valign: 'middle', margin: 0
        }});
        slide.addText(m.label || '', {{
          x: xPos + 0.15, y: 2.75, w: 2.4, h: 0.45,
          fontSize: 12, color: C.white, bold: true, align: 'center', wrap: true, margin: 0
        }});
        slide.addText(m.description || '', {{
          x: xPos + 0.12, y: 3.3, w: 2.46, h: 1.4,
          fontSize: 11, color: C.muted, align: 'center', wrap: true, margin: 6
        }});
      }});

    }} else if (slide_data.type === 'capabilities') {{
      slide.background = {{ color: C.white }};

      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 10, h: 0.9,
        fill: {{ color: C.navy }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.title, {{
        x: 0.4, y: 0.12, w: 8, h: 0.65,
        fontSize: 22, color: C.white, bold: true, margin: 0, valign: 'middle'
      }});
      slide.addText('PLATFORM', {{
        x: 8.0, y: 0.25, w: 1.7, h: 0.4,
        fontSize: 9, color: C.cyan, bold: true, charSpacing: 3, align: 'right', margin: 0
      }});

      const items = (slide_data.items || []).slice(0, 4);
      items.forEach((item, i) => {{
        const xPos = 0.4 + i * 2.4;
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: xPos, y: 1.05, w: 2.15, h: 4.2,
          fill: {{ color: C.lightBg }}, line: {{ color: C.blue, width: 0.4 }},
          shadow: makeShadow()
        }});
        slide.addShape(pres.shapes.OVAL, {{
          x: xPos + 0.575, y: 1.25, w: 1.0, h: 1.0,
          fill: {{ color: C.navy }}, line: {{ type: 'none' }}
        }});
        slide.addText(item.icon || '●', {{
          x: xPos + 0.575, y: 1.25, w: 1.0, h: 1.0,
          fontSize: 20, align: 'center', valign: 'middle', margin: 0
        }});
        slide.addText(item.title || '', {{
          x: xPos + 0.1, y: 2.45, w: 1.95, h: 0.55,
          fontSize: 12, color: C.navy, bold: true, align: 'center', wrap: true, margin: 0
        }});
        slide.addText(item.desc || '', {{
          x: xPos + 0.1, y: 3.1, w: 1.95, h: 1.9,
          fontSize: 10.5, color: '334466', align: 'center', wrap: true, margin: 6
        }});
      }});

    }} else if (slide_data.type === 'use_cases') {{
      slide.background = {{ color: C.offWhite }};

      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 10, h: 0.9,
        fill: {{ color: C.blue }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.title, {{
        x: 0.4, y: 0.12, w: 8, h: 0.65,
        fontSize: 22, color: C.white, bold: true, margin: 0, valign: 'middle'
      }});
      slide.addText('USE CASES', {{
        x: 7.8, y: 0.25, w: 1.9, h: 0.4,
        fontSize: 9, color: C.cyan, bold: true, charSpacing: 3, align: 'right', margin: 0
      }});

      const cases = (slide_data.use_cases || []).slice(0, 3);
      cases.forEach((uc, i) => {{
        const yPos = 1.1 + i * 1.45;
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: 0.4, y: yPos, w: 9.2, h: 1.2,
          fill: {{ color: C.white }}, line: {{ color: '00000008' }},
          shadow: makeShadow()
        }});
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: 0.4, y: yPos, w: 0.07, h: 1.2,
          fill: {{ color: C.cyan }}, line: {{ type: 'none' }}
        }});
        slide.addText('0' + (i + 1), {{
          x: 0.6, y: yPos, w: 0.7, h: 1.2,
          fontSize: 24, color: C.blue, bold: true, valign: 'middle', align: 'center', margin: 0
        }});
        slide.addText(uc.title || '', {{
          x: 1.4, y: yPos + 0.1, w: 7.8, h: 0.4,
          fontSize: 14, color: C.navy, bold: true, margin: 0
        }});
        slide.addText(uc.desc || '', {{
          x: 1.4, y: yPos + 0.52, w: 7.8, h: 0.58,
          fontSize: 12, color: '334466', wrap: true, margin: 0
        }});
      }});

    }} else if (slide_data.type === 'why_snaplogic') {{
      slide.background = {{ color: C.navy }};

      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 10, h: 0.9,
        fill: {{ color: C.blue }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.title || 'Why SnapLogic', {{
        x: 0.4, y: 0.12, w: 8, h: 0.65,
        fontSize: 22, color: C.white, bold: true, margin: 0, valign: 'middle'
      }});

      const reasons = (slide_data.reasons || []).slice(0, 4);
      reasons.forEach((r, i) => {{
        const yPos = 1.1 + i * 1.05;
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: 0.5, y: yPos, w: 9.0, h: 0.85,
          fill: {{ color: '0D2040' }}, line: {{ color: C.blue, width: 0.4 }},
          shadow: makeShadow()
        }});
        slide.addShape(pres.shapes.OVAL, {{
          x: 0.65, y: yPos + 0.17, w: 0.52, h: 0.52,
          fill: {{ color: C.cyan }}, line: {{ type: 'none' }}
        }});
        slide.addText('✓', {{
          x: 0.65, y: yPos + 0.17, w: 0.52, h: 0.52,
          fontSize: 11, color: C.navy, bold: true, align: 'center', valign: 'middle', margin: 0
        }});
        slide.addText(r, {{
          x: 1.35, y: yPos, w: 7.9, h: 0.85,
          fontSize: 13.5, color: C.white, valign: 'middle', wrap: true, margin: 0
        }});
      }});

      slide.addText(slide_data.tagline || '', {{
        x: 0.5, y: 5.1, w: 9.0, h: 0.4,
        fontSize: 12, color: C.cyan, italic: true, align: 'center', margin: 0
      }});

    }} else if (slide_data.type === 'next_steps') {{
      slide.background = {{ color: C.white }};

      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 0, w: 10, h: 0.9,
        fill: {{ color: C.navy }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.title || 'Next Steps', {{
        x: 0.4, y: 0.12, w: 8, h: 0.65,
        fontSize: 22, color: C.white, bold: true, margin: 0, valign: 'middle'
      }});
      slide.addText('ACTION PLAN', {{
        x: 7.5, y: 0.25, w: 2.2, h: 0.4,
        fontSize: 9, color: C.cyan, bold: true, charSpacing: 3, align: 'right', margin: 0
      }});

      const steps = (slide_data.steps || []).slice(0, 3);
      steps.forEach((s, i) => {{
        const xPos = 0.4 + i * 3.2;
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: xPos, y: 1.1, w: 2.9, h: 3.6,
          fill: {{ color: C.lightBg }}, line: {{ color: C.blue, width: 0.4 }},
          shadow: makeShadow()
        }});
        slide.addShape(pres.shapes.RECTANGLE, {{
          x: xPos, y: 1.1, w: 2.9, h: 0.06,
          fill: {{ color: C.cyan }}, line: {{ type: 'none' }}
        }});
        slide.addText(s.num || String(i+1).padStart(2,'0'), {{
          x: xPos, y: 1.2, w: 2.9, h: 0.9,
          fontSize: 40, color: C.blue, bold: true, align: 'center', margin: 0
        }});
        slide.addText(s.action || '', {{
          x: xPos + 0.15, y: 2.2, w: 2.6, h: 0.6,
          fontSize: 13, color: C.navy, bold: true, align: 'center', wrap: true, margin: 0
        }});
        slide.addText(s.desc || '', {{
          x: xPos + 0.15, y: 2.9, w: 2.6, h: 1.7,
          fontSize: 11, color: '334466', align: 'center', wrap: true, margin: 6
        }});
      }});

      // CTA bar
      slide.addShape(pres.shapes.RECTANGLE, {{
        x: 0, y: 4.9, w: 10, h: 0.725,
        fill: {{ color: C.navy }}, line: {{ type: 'none' }}
      }});
      slide.addText(slide_data.cta || 'Ready to transform your integrations?', {{
        x: 0.5, y: 4.9, w: 9, h: 0.725,
        fontSize: 15, color: C.cyan, bold: true, align: 'center', valign: 'middle', margin: 0
      }});
    }}
  }}

  await pres.writeFile({{ fileName: '/tmp/snaplogic_deck.pptx' }});
  console.log('DONE');
}}

buildDeck().catch(e => {{ console.error(e); process.exit(1); }});
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    customer = data.get('customer', '')
    snaplogic = data.get('snaplogic', '')
    slide_count = data.get('slideCount', 8)
    tone = data.get('tone', 'consultative')

    # Use Claude to generate slide content
    client = anthropic.Anthropic()
    
    prompt = SLIDE_GEN_PROMPT.format(
        customer=customer,
        snaplogic=snaplogic,
        slide_count=slide_count,
        tone=tone
    )
    
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = message.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[1]
        raw = raw.rsplit('```', 1)[0]
    
    slide_data = json.loads(raw)
    
    # Write the JS script
    js_code = PPTX_TEMPLATE.format(data=json.dumps(slide_data))
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_code)
        js_path = f.name
    
    result = subprocess.run(
        ['node', js_path],
        capture_output=True, text=True, timeout=60
    )
    
    os.unlink(js_path)
    
    if result.returncode != 0:
        return jsonify({'error': result.stderr}), 500
    
    return send_file(
        '/tmp/snaplogic_deck.pptx',
        as_attachment=True,
        download_name='SnapLogic_Pitch_Deck.pptx',
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
