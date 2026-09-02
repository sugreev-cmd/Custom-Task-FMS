# -*- coding: utf-8 -*-
"""Add camera -> Google Drive proof photos to Custom-Task-FMS.

Runs inside GitHub Actions. Patches index.html in place.
Safe to run again: if the patch is already applied it exits quietly.
"""
import sys, os

TARGET = 'index.html'

src = open(TARGET, encoding='utf-8').read()
orig = len(src)

if 'tfPhotoGrid' in src:
    print('Already patched - nothing to do.')
    sys.exit(0)

# ------------------------------------------------------------------ 1. CSS
CSS = """
/* PROOF PHOTOS (camera -> Drive) */
.tf-cam-wrap{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:8px 0 10px}
.tf-btn{display:inline-flex;align-items:center;gap:6px;padding:9px 14px;border-radius:8px;cursor:pointer;
  font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;transition:.18s;
  background:var(--s3);border:1px solid var(--bd2);color:var(--text)}
.tf-btn:hover{border-color:var(--teal);color:var(--teal)}
.tf-btn.cam{background:var(--teal2);border-color:rgba(0,191,165,.45);color:var(--teal)}
.tf-btn.cam:hover{background:rgba(0,191,165,.22)}
.tf-btn:disabled{opacity:.45;cursor:not-allowed}
.tf-count{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--dim);margin-left:auto}
.tf-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:8px}
.tf-ph{position:relative;border-radius:8px;overflow:hidden;background:var(--s3);border:1px solid var(--bd);
  aspect-ratio:3/4}
.tf-ph img{width:100%;height:100%;object-fit:cover;display:block}
.tf-ph.up{opacity:.75}
.tf-ph.bad{border-color:rgba(255,68,68,.6)}
.tf-ov{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  background:rgba(0,0,0,.55);color:#fff;font-size:10px;font-weight:600;letter-spacing:.4px}
.tf-ov.bad{background:rgba(160,20,20,.7)}
.tf-cap{position:absolute;left:0;right:0;bottom:0;background:linear-gradient(transparent,rgba(0,0,0,.82));
  color:#fff;font-size:8.5px;line-height:1.35;padding:12px 5px 4px;font-family:'JetBrains Mono',monospace}
.tf-del{position:absolute;top:4px;right:4px;width:20px;height:20px;border-radius:50%;border:none;cursor:pointer;
  background:rgba(0,0,0,.6);color:#fff;font-size:10px;line-height:1;display:flex;align-items:center;justify-content:center}
.tf-del:hover{background:#DC2626}
.tf-open{position:absolute;top:4px;left:4px;width:20px;height:20px;border-radius:50%;
  background:rgba(0,0,0,.6);color:#fff;font-size:10px;text-decoration:none;display:flex;align-items:center;justify-content:center}
.tf-open:hover{background:var(--teal);color:#08131c}
.tf-empty{grid-column:1/-1;text-align:center;padding:16px 10px;color:var(--dim);font-size:11px;line-height:1.6}
.tf-warn{background:rgba(255,184,0,.1);border:1px solid rgba(255,184,0,.35);color:#FFB800;border-radius:8px;
  padding:9px 11px;font-size:11px;line-height:1.55;margin-bottom:8px}
</style>"""
assert src.count('</style>') == 1
src = src.replace('</style>', CSS, 1)

# ------------------------------------------------------------------ 2. Proof box markup
OLD_BOX = """      <div class="proof-link-box" id="proofLinkBox">
        <div class="proof-link-lbl">\U0001F517 Proof Link (Optional)</div>
        <input class="proof-link-inp" id="taskProofLink" placeholder="https://drive.google.com/..." type="url">
        <div id="proofLinkView" style="display:none"></div>
      </div>"""
NEW_BOX = """      <div class="proof-link-box" id="proofLinkBox">
        <div class="proof-link-lbl">\U0001F4F7 Proof Photos</div>
        <div class="tf-warn" id="tfNoUrlWarn" style="display:none">Proof upload set nahi hai. Settings -> Data me
          <b>Proof Upload Script URL</b> daal dijiye, phir camera chalu ho jayega.</div>
        <div class="tf-cam-wrap" id="tfCamWrap">
          <button type="button" class="tf-btn cam" id="tfCamBtn">\U0001F4F7 Take Photo</button>
          <button type="button" class="tf-btn" id="tfGalBtn">\U0001F5BC Choose Photo</button>
          <span class="tf-count" id="tfCount"></span>
        </div>
        <input type="file" id="tfCamInput" accept="image/*" capture="environment" style="display:none">
        <input type="file" id="tfGalInput" accept="image/*" multiple style="display:none">
        <div class="tf-grid" id="tfPhotoGrid"></div>
        <div class="proof-link-lbl" style="margin-top:14px">\U0001F517 Proof Link (manual, optional)</div>
        <input class="proof-link-inp" id="taskProofLink" placeholder="https://drive.google.com/..." type="url">
        <div id="proofLinkView" style="display:none"></div>
      </div>"""
assert src.count(OLD_BOX) == 1
src = src.replace(OLD_BOX, NEW_BOX, 1)

# ------------------------------------------------------------------ 3. Settings input
OLD_SET = """      <button class="sp-btn" id="saveDbBtn">\U0001F4BE Save &amp; Reconnect</button>"""
NEW_SET = """      <div class="sp-label">Proof Upload Script URL <span style="color:var(--dim);text-transform:none;letter-spacing:0">- camera se photo Drive me bhejne ke liye</span></div>
      <input class="sp-input" id="sp-proof-url" placeholder="https://script.google.com/macros/s/AKfy.../exec">
      <button class="sp-btn" id="saveDbBtn">\U0001F4BE Save &amp; Reconnect</button>"""
assert src.count(OLD_SET) == 1
src = src.replace(OLD_SET, NEW_SET, 1)

# ------------------------------------------------------------------ 4. Row mapping
A = ",proofLink:r.proof_link||''};}"
assert src.count(A) == 1
src = src.replace(A, ",proofLink:r.proof_link||'',proofPhotos:Array.isArray(r.proof_photos)?r.proof_photos:[]};}", 1)

B = "proof_link:task.proofLink||'',updated_at:"
assert src.count(B) == 1
src = src.replace(B, "proof_link:task.proofLink||'',proof_photos:task.proofPhotos||[],updated_at:", 1)

C = "proof_link:t.proofLink||'',updated_at:"
assert src.count(C) == 1
src = src.replace(C, "proof_link:t.proofLink||'',proof_photos:t.proofPhotos||[],updated_at:", 1)

# ------------------------------------------------------------------ 5. Modal open / save hooks
D = "document.getElementById('taskProofLink').value=t.proofLink||'';"
assert src.count(D) == 1
src = src.replace(D, D + "tfLoadPhotos(t);", 1)

E = "document.getElementById('taskProofLink').disabled=_ro;"
assert src.count(E) == 1
src = src.replace(E, E + "tfSetReadOnly(_ro);", 1)

F = "t.proofLink=document.getElementById('taskProofLink').value;"
assert src.count(F) == 1
src = src.replace(F, "t.proofLink=document.getElementById('taskProofLink').value;t.proofPhotos=tfCleanPhotos();"
                     "if(!t.proofLink&&t.proofPhotos.length)t.proofLink=t.proofPhotos[0].viewUrl||'';", 1)

# ------------------------------------------------------------------ 6. Settings read / write
G = "setVal('sp-db-table',d.table);"
assert src.count(G) == 1
src = src.replace(G, G + "setVal('sp-proof-url',(SETTINGS&&SETTINGS.proofScriptUrl)||'');", 1)

H = """  saveSettings(SETTINGS);applyDb();renderDbInputs();"""
assert src.count(H) == 1
src = src.replace(H, """  var _pu=document.getElementById('sp-proof-url');
  SETTINGS.proofScriptUrl=_pu?_pu.value.trim():(SETTINGS.proofScriptUrl||'');
  saveSettings(SETTINGS);applyDb();renderDbInputs();""", 1)

# ------------------------------------------------------------------ 7. JS module
JS = r"""
/* ==============================================================
   PROOF PHOTOS  -  camera -> stamp -> Google Drive -> link saved
   Upload endpoint: Apps Script web app (Settings -> Data)
   ============================================================== */

var tfPhotos = [];                 // photos of the task currently open
var TF_MAX_SIDE = 1400;            // px - long edge after resize
var TF_QUALITY  = 0.82;            // jpeg quality
var TF_TIMEOUT  = 60000;           // ms

function tfScriptUrl(){
  var u = (typeof SETTINGS === 'object' && SETTINGS) ? (SETTINGS.proofScriptUrl || '') : '';
  return String(u).trim();
}

function tfLoadPhotos(t){
  tfPhotos = (t && Array.isArray(t.proofPhotos)) ? t.proofPhotos.slice() : [];
  var warn = document.getElementById('tfNoUrlWarn');
  var wrap = document.getElementById('tfCamWrap');
  var has  = !!tfScriptUrl();
  if(warn) warn.style.display = has ? 'none' : 'block';
  if(wrap) wrap.style.opacity = has ? '1' : '.5';
  tfRenderPhotos();
}

function tfSetReadOnly(ro){
  var wrap = document.getElementById('tfCamWrap');
  if(wrap) wrap.style.display = ro ? 'none' : 'flex';
  tfRenderPhotos();
}

function tfCleanPhotos(){
  return tfPhotos.filter(function(p){ return p && p.viewUrl; }).map(function(p){
    return { fileId:p.fileId||'', viewUrl:p.viewUrl, thumbnailUrl:p.thumbnailUrl||'',
             at:p.at||'', by:p.by||'' };
  });
}

function tfRenderPhotos(){
  var g = document.getElementById('tfPhotoGrid');
  if(!g) return;
  var ro = (typeof isRO === 'function') ? isRO() : false;
  var cnt = document.getElementById('tfCount');
  var okN = tfPhotos.filter(function(p){ return p && p.viewUrl; }).length;
  if(cnt) cnt.textContent = tfPhotos.length ? (okN + ' photo' + (okN===1?'':'s')) : '';

  if(!tfPhotos.length){
    g.innerHTML = '<div class="tf-empty">' +
      (ro ? 'Koi proof photo nahi lagi.' :
            'Koi photo nahi lagi.<br><b>Take Photo</b> dabaiye - camera khulega, photo apne aap Drive me chali jayegi.') +
      '</div>';
    return;
  }

  g.innerHTML = tfPhotos.map(function(p,i){
    var src = p.thumbnailUrl || p.local || '';
    var h = '<div class="tf-ph'+(p.uploading?' up':'')+(p.failed?' bad':'')+'">';
    h += src ? '<img src="'+escH(src)+'" loading="lazy" onerror="this.style.opacity=.2">' : '';
    if(p.uploading) h += '<div class="tf-ov">Uploading...</div>';
    else if(p.failed) h += '<div class="tf-ov bad">Failed</div>';
    if(p.viewUrl) h += '<a class="tf-open" href="'+escH(p.viewUrl)+'" target="_blank" rel="noopener" title="Open in Drive" onclick="event.stopPropagation()">↗</a>';
    if(!ro) h += '<button type="button" class="tf-del" title="Remove" onclick="tfRemovePhoto('+i+')">✕</button>';
    h += '<div class="tf-cap">'+escH(p.at||'')+(p.by?'<br>'+escH(p.by):'')+'</div>';
    h += '</div>';
    return h;
  }).join('');
}

function tfRemovePhoto(i){
  var p = tfPhotos[i];
  if(!p) return;
  if(p.uploading){ showToast('Ye photo abhi upload ho rahi hai','e'); return; }
  if(!confirm('Ye photo list se hata dein?\n\n(Drive me file rahegi, sirf task se hatt jayegi.)')) return;
  tfPhotos.splice(i,1);
  tfRenderPhotos();
}

/* date / time of capture */
function tfFmtDT(d){
  var M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var hh=d.getHours(), ap=hh>=12?'PM':'AM', h12=hh%12; if(h12===0)h12=12;
  return d.getDate()+' '+M[d.getMonth()]+' '+d.getFullYear()+',  '+
         (h12<10?'0':'')+h12+':'+String(d.getMinutes()).padStart(2,'0')+' '+ap;
}
function tfDateKey(d){
  return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
}
function tfMeta(file, t){
  /* A camera photo carries its capture time in lastModified. */
  var d = (file && file.lastModified) ? new Date(file.lastModified) : new Date();
  if(isNaN(d.getTime())) d = new Date();
  if(Math.abs(Date.now() - d.getTime()) > 86400000) d = new Date();

  var sel = document.getElementById('taskAssign');
  var who = (sel && sel.value) || (t && t.assign) || '';
  if(!who && typeof curRole === 'function' && curRole()) who = curRole().name || '';
  return { when:d, at:tfFmtDT(d), by:who || '-', task:(t && t.name) || '' };
}

/* resize + stamp date/time and name onto the picture */
function tfProcess(file, meta){
  return new Promise(function(resolve, reject){
    var fr = new FileReader();
    fr.onerror = function(){ reject(new Error('Photo padhi nahi ja saki')); };
    fr.onload = function(){
      var img = new Image();
      img.onerror = function(){ reject(new Error('Photo kholi nahi ja saki')); };
      img.onload = function(){
        try{
          var w = img.width, h = img.height;
          var s = Math.min(1, TF_MAX_SIDE / Math.max(w, h));
          w = Math.max(1, Math.round(w*s)); h = Math.max(1, Math.round(h*s));

          var c = document.createElement('canvas');
          c.width = w; c.height = h;
          var x = c.getContext('2d');
          x.drawImage(img, 0, 0, w, h);

          var pad = Math.round(Math.max(10, w*0.022));
          var f1  = Math.round(Math.max(13, w*0.031));
          var f2  = Math.round(f1*0.82);
          var l1  = meta.at;
          var l2  = meta.by + (meta.task ? '  ·  ' + meta.task : '');
          var barH = pad*2 + f1 + f2 + Math.round(f1*0.30);

          x.fillStyle = 'rgba(0,0,0,0.58)';
          x.fillRect(0, h-barH, w, barH);

          x.textBaseline = 'top';
          x.fillStyle = '#FFFFFF';
          x.font = '700 ' + f1 + 'px "DM Sans", Arial, sans-serif';
          x.fillText(l1, pad, h-barH+pad);
          x.fillStyle = 'rgba(255,255,255,0.88)';
          x.font = '400 ' + f2 + 'px "DM Sans", Arial, sans-serif';
          x.fillText(l2, pad, h-barH+pad+f1+Math.round(f1*0.28));

          resolve(c.toDataURL('image/jpeg', TF_QUALITY));
        }catch(err){ reject(err); }
      };
      img.src = fr.result;
    };
    fr.readAsDataURL(file);
  });
}

/* POST to the Apps Script web app */
function tfPost(payload){
  var url = tfScriptUrl();
  if(!url) return Promise.reject(new Error('Settings me Proof Upload Script URL nahi hai'));
  var ctrl = new AbortController();
  var timer = setTimeout(function(){ ctrl.abort(); }, TF_TIMEOUT);
  return fetch(url, { method:'POST', body: JSON.stringify(payload), signal: ctrl.signal })
    .then(function(r){
      if(!r.ok) throw new Error('Server error ' + r.status);
      return r.text();
    })
    .then(function(txt){
      var j;
      try { j = JSON.parse(txt); }
      catch(e){ throw new Error('Apps Script ne galat jawab bheja - deployment / permission check karein'); }
      return j;
    })
    .catch(function(e){
      if(e && e.name === 'AbortError') throw new Error('Timeout - upload poora nahi hua, network dekh lein');
      throw e;
    })
    .then(function(v){ clearTimeout(timer); return v; },
          function(e){ clearTimeout(timer); throw e; });
}

/* main handler */
function tfHandleFiles(fileList){
  var t = (typeof tasks !== 'undefined') ? tasks.filter(function(x){ return x.id === viewingTaskId; })[0] : null;
  if(!t) return;
  if(!tfScriptUrl()){
    showToast('Pehle Settings -> Data me Proof Upload Script URL daalein','e');
    return;
  }
  var files = Array.prototype.slice.call(fileList || []);
  if(!files.length) return;

  files.reduce(function(chain, file){
    return chain.then(function(){
      if(!/^image\//.test(file.type || '')){
        showToast('Sirf photo lag sakti hai','e');
        return;
      }
      var meta  = tfMeta(file, t);
      var entry = { local:'', uploading:true, failed:false, at:meta.at, by:meta.by };
      tfPhotos.push(entry);
      tfRenderPhotos();

      return tfProcess(file, meta).then(function(dataUrl){
        entry.local = dataUrl;
        tfRenderPhotos();
        var safe = function(s){ return String(s||'').replace(/[^\w\s-]/g,'').replace(/\s+/g,' ').trim().slice(0,40); };
        var fname = safe(t.name) + '__' + safe(meta.by) + '__' +
                    String(meta.when.getHours()).padStart(2,'0') + String(meta.when.getMinutes()).padStart(2,'0') +
                    '__' + Date.now() + '.jpg';
        return tfPost({
          action: 'uploadProof',
          imageData: dataUrl,
          fileName: fname,
          dateKey: tfDateKey(meta.when),
          description: (t.name||'') + ' | ' + meta.at + ' | ' + meta.by
        });
      }).then(function(r){
        if(r && r.success){
          entry.uploading = false;
          entry.fileId = r.fileId;
          entry.viewUrl = r.viewUrl;
          entry.thumbnailUrl = r.thumbnailUrl;
          entry.shared = !!r.shared;
          if(r.shared === false){
            showToast('Photo Drive me chali gayi, par link sabke liye open nahi hua','e');
          }
          var linkBox = document.getElementById('taskProofLink');
          if(linkBox && !linkBox.value) linkBox.value = r.viewUrl;
        } else {
          throw new Error((r && r.error) || 'Upload fail');
        }
      }).catch(function(err){
        entry.uploading = false;
        entry.failed = true;
        showToast('Photo upload fail - ' + (err.message || err), 'e');
      }).then(function(){
        tfRenderPhotos();
      });
    });
  }, Promise.resolve()).then(function(){
    var okN = tfPhotos.filter(function(p){ return p.viewUrl; }).length;
    if(okN) showToast('✓ ' + okN + ' photo taiyar - ab Mark Done ya Save dabaiye','s');
  });
}

/* wire up (wait for the DOM so the buttons actually exist) */
(function tfWire(){
  function attach(){
    var on = function(id, ev, fn){ var e = document.getElementById(id); if(e) e.addEventListener(ev, fn); };
    on('tfCamBtn','click', function(){ var i=document.getElementById('tfCamInput'); if(i){ i.value=''; i.click(); } });
    on('tfGalBtn','click', function(){ var i=document.getElementById('tfGalInput'); if(i){ i.value=''; i.click(); } });
    on('tfCamInput','change', function(e){ tfHandleFiles(e.target.files); e.target.value=''; });
    on('tfGalInput','change', function(e){ tfHandleFiles(e.target.files); e.target.value=''; });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', attach);
  else attach();
})();
</script>"""

JS_ANCHOR = "\n</script>"
assert src.count(JS_ANCHOR) == 1, src.count(JS_ANCHOR)
src = src.replace(JS_ANCHOR, "\n" + JS, 1)

open(TARGET,'w',encoding='utf-8').write(src)
print('Patched %s: %d -> %d chars (+%d)' % (TARGET, orig, len(src), len(src)-orig))
