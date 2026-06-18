// =============================================================
// Tyler Loans — Google Drive Doc Uploader
// Receives POSTed .docx files and saves them to a Drive folder
// as Google Docs (auto-converted on upload).
// =============================================================
//
// Setup (~2 min, one time):
// 1. Go to https://script.google.com
// 2. Click "New project"
// 3. Delete the default code, paste THIS ENTIRE FILE
// 4. Click the floppy-disk Save icon
// 5. Top right: "Deploy" → "New deployment"
// 6. Click the gear icon next to "Select type" → "Web app"
// 7. Description: "Tyler Blog Doc Uploader"
//    Execute as: Me (your gmail)
//    Who has access: Anyone
// 8. Click "Deploy"
// 9. Authorize when prompted (it'll warn "unverified" — click
//    "Advanced" → "Go to project (unsafe)" — it's safe because
//    YOU wrote the script and YOU control where files land)
// 10. Copy the "Web app URL" and paste it back to Claude
//
// =============================================================

// Folder name in your Drive where new blog drafts will land.
// Folder is auto-created if it doesn't exist.
const TARGET_FOLDER = 'Tyler Blog Drafts';

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const filename = payload.filename || 'Untitled.docx';
    const base64 = payload.content;
    if (!base64) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false, error: 'Missing content field'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // Decode and create blob
    const bytes = Utilities.base64Decode(base64);
    const blob = Utilities.newBlob(bytes, MimeType.MICROSOFT_WORD, filename);

    // Find or create the target folder
    let folder;
    const folders = DriveApp.getFoldersByName(TARGET_FOLDER);
    if (folders.hasNext()) {
      folder = folders.next();
    } else {
      folder = DriveApp.createFolder(TARGET_FOLDER);
    }

    // Upload + auto-convert to Google Doc
    const resource = {
      name: filename.replace(/\.docx$/i, ''),
      parents: [folder.getId()],
      mimeType: MimeType.GOOGLE_DOCS
    };
    const doc = Drive.Files.create(resource, blob, { supportsAllDrives: true });

    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      file_id: doc.id,
      url: 'https://docs.google.com/document/d/' + doc.id + '/edit'
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// Health check — visit the webhook URL in browser to verify it's live.
function doGet() {
  return ContentService.createTextOutput(JSON.stringify({
    status: 'online',
    target_folder: TARGET_FOLDER
  })).setMimeType(ContentService.MimeType.JSON);
}
