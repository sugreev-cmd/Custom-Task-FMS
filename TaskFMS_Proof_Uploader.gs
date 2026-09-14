/**
 * ============================================================
 *  TASK FMS - PROOF PHOTO UPLOADER   (v2 - fast)
 * ============================================================
 *
 *  Ye script Task FMS se aayi hui photo ko aapke Google Drive
 *  me save karta hai aur uska link wapas bhej deta hai.
 *
 *  Drive me aise structure banega (apne aap):
 *
 *      Task FMS Proofs /
 *          2026-08-27 /
 *              Hall 4 Cleaning floors__Vandana__1430.jpg
 *
 *  ------------------------------------------------------------
 *  v2 me kya badla (speed ke liye)
 *  ------------------------------------------------------------
 *  1. Sharing ab har file par nahi, sirf FOLDER par ek baar hoti hai.
 *     Andar ki saari files folder se sharing khud le leti hain.
 *     -> har photo se ek poora Drive write kam (~1-2 second bacha)
 *
 *  2. Folder ka ID CacheService me 6 ghante ke liye yaad rakha jata hai.
 *     Pehle har photo par 2 Drive queries chalti thi folder dhoondhne me.
 *     -> ~1 second aur bacha
 *
 *  Baaki sab kuch bilkul pehle jaisa hai - wahi folder, wahi file name,
 *  wahi "anyone with the link" sharing, wahi response format.
 *
 *  ------------------------------------------------------------
 *  DEPLOY KAISE KAREIN
 *  ------------------------------------------------------------
 *  Pehli baar:
 *  1. script.google.com kholein -> New project
 *  2. Saara default code hata kar ye poori file paste karein
 *  3. Save -> project ka naam "Task FMS Proof Uploader" rakh dein
 *  4. Upar dayein -> Deploy -> New deployment
 *  5. gear icon -> Web app
 *  6. Execute as        : Me
 *     Who has access    : Anyone            <-- ye zaroori hai
 *  7. Deploy -> Authorize access -> apna account chunein ->
 *     "Advanced" -> "Go to ... (unsafe)" -> Allow
 *  8. Jo URL mile use Task FMS ke Settings -> Data me paste kar dein
 *
 *  Update karte waqt (v1 se v2):
 *  1. script.google.com -> apna project kholein
 *  2. purana code hata kar ye poori file paste karein -> Save
 *  3. Deploy -> Manage deployments -> pencil (Edit)
 *  4. Version: "New version" chunein -> Deploy
 *  URL wahi rahega, Task FMS me kuch badalna nahi padega.
 * ============================================================
 */

var CONFIG = {
  ROOT_FOLDER_NAME: 'Task FMS Proofs',
  DAY_FOLDERS: true,
  MAKE_LINK_VIEWABLE: true,

  /* true  = sharing folder par ek baar (TEZ - recommended)
     false = purana tareeka, har file par alag se sharing (SLOW) */
  SHARE_AT_FOLDER: true,

  FOLDER_CACHE_SECONDS: 21600   /* 6 ghante */
};


function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return out({ success: false, error: 'Empty request' });
    }

    var p = JSON.parse(e.postData.contents);

    if (p.action !== 'uploadProof') {
      return out({ success: false, error: 'Unknown action: ' + p.action });
    }

    var b64 = String(p.imageData || '').replace(/^data:image\/[a-z]+;base64,/i, '');
    if (!b64) return out({ success: false, error: 'No image data received' });

    var bytes = Utilities.base64Decode(b64);
    var name = safeName(p.fileName || ('proof_' + Date.now() + '.jpg'));
    var blob = Utilities.newBlob(bytes, 'image/jpeg', name);

    var folder = targetFolder_(p.dateKey);
    var file = folder.createFile(blob);

    if (p.description) {
      try { file.setDescription(String(p.description).slice(0, 500)); } catch (ignore) {}
    }

    /* Folder pehle se "anyone with link" par set hai, is liye file
       usi se sharing le leti hai. Per-file setSharing sirf tab chalta
       hai jab SHARE_AT_FOLDER band ho. */
    var shared = false;
    if (CONFIG.MAKE_LINK_VIEWABLE) {
      if (CONFIG.SHARE_AT_FOLDER) {
        shared = true;
      } else {
        try {
          file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
          shared = true;
        } catch (shareErr) {
          shared = false;
        }
      }
    }

    var id = file.getId();
    return out({
      success: true,
      fileId: id,
      viewUrl: 'https://drive.google.com/file/d/' + id + '/view',
      thumbnailUrl: 'https://drive.google.com/thumbnail?id=' + id + '&sz=w600',
      folder: folder.getName(),
      shared: shared
    });

  } catch (err) {
    return out({ success: false, error: String(err && err.message ? err.message : err) });
  }
}


function doGet() {
  return out({
    success: true,
    status: 'Task FMS Proof Uploader v2 chal raha hai',
    folder: CONFIG.ROOT_FOLDER_NAME,
    shareAtFolder: CONFIG.SHARE_AT_FOLDER,
    time: new Date().toISOString()
  });
}


function out(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}


/**
 * Aaj ka folder deta hai. ID cache me rehta hai, is liye har photo par
 * Drive me folder dhoondhna nahi padta.
 */
function targetFolder_(dateKey) {
  var day = String(dateKey || '').match(/^\d{4}-\d{2}-\d{2}$/)
    ? dateKey
    : Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');

  var key = 'tffms_' + (CONFIG.DAY_FOLDERS ? day : 'root');
  var cache = null;
  try { cache = CacheService.getScriptCache(); } catch (ignore) {}

  if (cache) {
    var cachedId = cache.get(key);
    if (cachedId) {
      try {
        var cached = DriveApp.getFolderById(cachedId);
        if (!cached.isTrashed()) return cached;
      } catch (staleErr) { /* folder hat gaya - neeche dobara ban jayega */ }
    }
  }

  var root = getOrCreate_(DriveApp.getRootFolder(), CONFIG.ROOT_FOLDER_NAME);
  var folder = CONFIG.DAY_FOLDERS ? getOrCreate_(root, day) : root;

  if (CONFIG.MAKE_LINK_VIEWABLE && CONFIG.SHARE_AT_FOLDER) {
    try {
      folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    } catch (shareErr) { /* admin ne link-sharing band ki hui ho sakti hai */ }
  }

  if (cache) {
    try { cache.put(key, folder.getId(), CONFIG.FOLDER_CACHE_SECONDS); } catch (ignore) {}
  }
  return folder;
}


function getOrCreate_(parent, name) {
  var it = parent.getFoldersByName(name);
  while (it.hasNext()) {
    var f = it.next();
    if (!f.isTrashed()) return f;
  }
  return parent.createFolder(name);
}


function safeName(n) {
  return String(n).replace(/[\\\/:*?"<>|]/g, '_').replace(/\s+/g, ' ').trim().slice(0, 120);
}


/**
 * Editor me ise ek baar Run karke dekh lein - Drive me ek test file
 * banegi aur Execution log me result dikhega.
 */
function runSelfTest() {
  var png =
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';

  var t0 = new Date().getTime();
  var res = doPost({
    postData: {
      contents: JSON.stringify({
        action: 'uploadProof',
        imageData: 'data:image/png;base64,' + png,
        fileName: 'SELF_TEST_delete_me.jpg',
        dateKey: Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd'),
        description: 'Self test'
      })
    }
  });

  Logger.log(res.getContent());
  Logger.log('Time taken: ' + (new Date().getTime() - t0) + ' ms');
}


/**
 * Ise ek baar Run karke aaj ka folder pehle se bana aur share kar dein,
 * taaki din ki pehli photo bhi turant chali jaye.
 * Chahein to isko daily time-driven trigger par laga sakte hain.
 */
function warmUpToday() {
  var f = targetFolder_(null);
  Logger.log('Ready: ' + f.getName() + '  (' + f.getId() + ')');
}
