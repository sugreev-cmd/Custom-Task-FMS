/**
 * ============================================================
 *  TASK FMS - PROOF PHOTO UPLOADER
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
 *  DEPLOY KAISE KAREIN  (ek hi baar karna hai)
 *  ------------------------------------------------------------
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
 * ============================================================
 */

var CONFIG = {
  ROOT_FOLDER_NAME: 'Task FMS Proofs',
  DAY_FOLDERS: true,
  MAKE_LINK_VIEWABLE: true
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

    var shared = false;
    if (CONFIG.MAKE_LINK_VIEWABLE) {
      try {
        file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
        shared = true;
      } catch (shareErr) {
        shared = false;
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
    status: 'Task FMS Proof Uploader chal raha hai',
    folder: CONFIG.ROOT_FOLDER_NAME,
    time: new Date().toISOString()
  });
}


function out(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}


function targetFolder_(dateKey) {
  var root = getOrCreate_(DriveApp.getRootFolder(), CONFIG.ROOT_FOLDER_NAME);
  if (!CONFIG.DAY_FOLDERS) return root;

  var day = String(dateKey || '').match(/^\d{4}-\d{2}-\d{2}$/)
    ? dateKey
    : Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');

  return getOrCreate_(root, day);
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
}
