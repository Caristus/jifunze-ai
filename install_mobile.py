import re, socket
from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
bp = base / "templates/base.html"
html = bp.read_text(encoding="utf-8")
HEAD = '''<!-- JF_MOBILE_HEAD -->
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1B1F4B">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
'''
if "JF_MOBILE_HEAD" not in html:
    if re.search(r'<meta[^>]+name=["\']viewport["\']', html):
        html = re.sub(r'<meta[^>]+name=["\']viewport["\'][^>]*>', HEAD.strip(), html, count=1)
    else:
        html = html.replace("</head>", HEAD + "</head>", 1)
LAYER = r'''<!-- JF_MOBILE_LAYER -->
<style>
  #mTopBar,#mTabBar,#mDrawer,#mScrim{display:none;}
  .m-link{display:flex;align-items:center;gap:.6rem;padding:.7rem .75rem;border-radius:.65rem;font-weight:600;font-size:.92rem;color:var(--ink,#0F172A);text-decoration:none;}
  .m-link.active{background:var(--soft,#F6F4EC);color:var(--indigo,#1B1F4B);}
  .m-tab{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font-size:.6rem;font-weight:700;color:var(--mut,#64748B);text-decoration:none;border:none;background:none;cursor:pointer;}
  .m-tab.active{color:var(--indigo,#1B1F4B);}
  .m-tab svg{width:21px;height:21px;}
  @media (max-width:767px){
    html,body{overflow-x:hidden;}
    body{padding-top:52px;padding-bottom:calc(62px + env(safe-area-inset-bottom,0px));}
    header{display:none!important;}
    #mTopBar{display:flex;position:fixed;top:0;left:0;right:0;height:52px;z-index:60;background:var(--indigo,#1B1F4B);color:#fff;align-items:center;gap:.7rem;padding:0 .8rem;padding-top:env(safe-area-inset-top,0px);box-shadow:0 2px 12px rgba(15,23,42,.28);}
    #mTabBar{display:flex;position:fixed;bottom:0;left:0;right:0;height:calc(62px + env(safe-area-inset-bottom,0px));padding-bottom:env(safe-area-inset-bottom,0px);background:#fff;border-top:1px solid var(--line,#E4E1D6);z-index:60;}
    #mScrim{position:fixed;inset:0;background:rgba(15,23,42,.45);z-index:70;opacity:0;pointer-events:none;transition:opacity .22s;}
    #mScrim.open{display:block;opacity:1;pointer-events:auto;}
    #mDrawer{display:flex;flex-direction:column;position:fixed;top:0;bottom:0;left:0;width:min(84vw,320px);background:var(--bg,#FDFCF8);z-index:80;transform:translateX(-105%);transition:transform .25s ease;padding:1rem .9rem;overflow-y:auto;box-shadow:0 0 40px rgba(15,23,42,.25);}
    #mDrawer.open{transform:none;}
    button,select,input,textarea,.jf-btn,.aa-btn{min-height:44px;}
    input,select,textarea{font-size:16px;}
    table{display:block;overflow-x:auto;-webkit-overflow-scrolling:touch;}
    [style*="sticky"]{position:static!important;max-height:none!important;overflow:visible!important;}
    h1{font-size:clamp(1.45rem,6.5vw,2.1rem)!important;}
    #doc{padding:1.1rem!important;}
    .max-w-7xl,.max-w-4xl,.max-w-3xl{padding-left:.85rem!important;padding-right:.85rem!important;}
    .aa-bar{gap:.4rem;}
    .aa-btn{flex:1 1 46%;justify-content:center;}
  }
</style>
<div id="mScrim"></div>
<aside id="mDrawer" aria-label="Main menu">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.7rem">
    <span style="font-family:Manrope,Inter,sans-serif;font-weight:800;color:var(--indigo,#1B1F4B);font-size:1.05rem">JIFUNZE AI</span>
    <button id="mClose" aria-label="Close menu" style="border:none;background:none;cursor:pointer;color:var(--mut,#64748B);min-height:36px">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </button>
  </div>
  <div id="mLinks" style="display:flex;flex-direction:column;gap:.15rem"></div>
  <div id="mControls" style="margin-top:1rem;display:flex;flex-direction:column;gap:.6rem;padding-top:.9rem;border-top:1px solid var(--line,#E4E1D6)"></div>
</aside>
<div id="mTopBar">
  <button id="mOpen" aria-label="Open menu" style="background:none;border:none;color:#fff;cursor:pointer;min-height:40px">
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
  </button>
  <span style="font-family:Manrope,Inter,sans-serif;font-weight:800;letter-spacing:.02em">JIFUNZE AI</span>
  <span id="mPage" style="margin-left:auto;font-size:.7rem;opacity:.85;text-align:right"></span>
</div>
<nav id="mTabBar" aria-label="Primary">
  <a class="m-tab" data-path="/" href="/"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>Home</a>
  <a class="m-tab" data-path="/learn/" href="/learn/"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>Companion</a>
  <a class="m-tab" data-path="/studio/" href="/studio/"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M18.4 5.6l-2.1 2.1M21 12h-3M18.4 18.4l-2.1-2.1M12 21v-3M5.6 18.4l2.1-2.1M3 12h3M5.6 5.6l2.1 2.1"/></svg>Studio</a>
  <a class="m-tab" data-path="/library/" href="/library/"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>Library</a>
  <button class="m-tab" id="mMore"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/></svg>More</button>
</nav>
<script>
(function(){
  var drawer=document.getElementById("mDrawer"),scrim=document.getElementById("mScrim"),
      links=document.getElementById("mLinks"),controls=document.getElementById("mControls"),
      header=document.querySelector("header"),page=document.getElementById("mPage");
  function openD(){drawer.classList.add("open");scrim.classList.add("open");}
  function closeD(){drawer.classList.remove("open");scrim.classList.remove("open");}
  document.getElementById("mOpen").onclick=openD;
  document.getElementById("mMore").onclick=openD;
  document.getElementById("mClose").onclick=closeD;
  scrim.onclick=closeD;
  var path=location.pathname;
  var anchors=header?Array.prototype.slice.call(header.querySelectorAll("a")):[];
  var seen={};
  anchors.forEach(function(a){
    var t=(a.textContent||"").trim();
    var h=a.getAttribute("href")||"";
    if(!t||t==="JIFUNZE AI"||t.length<3||seen[h])return;
    if(!h.startsWith("/")&&!h.startsWith("http"))return;
    seen[h]=1;
    var el=document.createElement("a");
    el.className="m-link"+(path===h|| (h!=="/"&&path.indexOf(h)===0) ?" active":"");
    el.href=h;el.textContent=t;
    links.appendChild(el);
    if(path===h||(h!=="/"&&path.indexOf(h)===0))page.textContent=t;
  });
  if(!page.textContent)page.textContent="Home";
  document.querySelectorAll("#mTabBar .m-tab[data-path]").forEach(function(t){
    if(t.dataset.path==="/" ? path==="/" : path.indexOf(t.dataset.path)===0)t.classList.add("active");
  });
  var selHome=header?Array.prototype.slice.call(header.querySelectorAll("select")).map(function(s){return {el:s,parent:s.parentNode,next:s.nextSibling};}):[];
  var mq=window.matchMedia("(max-width:767px)");
  function apply(){
    if(mq.matches){
      selHome.forEach(function(o){controls.appendChild(o.el);});
    }else{
      selHome.forEach(function(o){o.parent.insertBefore(o.el,o.next);});
      closeD();
    }
  }
  if(mq.addEventListener)mq.addEventListener("change",apply);else mq.addListener(apply);
  apply();
})();
</script>
'''
if "JF_MOBILE_LAYER" not in html:
    html = html.replace("</body>", LAYER + "</body>", 1)
    bp.write_text(html, encoding="utf-8")
sp = base / "config/settings.py"
st = sp.read_text(encoding="utf-8")
if "JF_LAN_HOST" not in st:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = None
    if ip:
        st += '\n# JF_LAN_HOST - allow phones on the local network during development\nALLOWED_HOSTS = list(ALLOWED_HOSTS) + ["%s"]\n' % ip
        sp.write_text(st, encoding="utf-8")
        print("LAN HOST ADDED:", ip)
print("MOBILE UI LAYER INSTALLED")
