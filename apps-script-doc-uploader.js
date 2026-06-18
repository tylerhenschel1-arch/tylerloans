// =============================================================
// Tyler Loans — Google Drive Doc Uploader (v2)
// Receives POSTed .docx files and saves them to a Drive folder
// as Google Docs. Uses only DriveApp — no advanced services needed.
// =============================================================

const TARGET_FOLDER = 'Tyler Blog Drafts';

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const filename = payload.filename || 'Untitled.docx';
    const base64 = payload.content;
    if (!base64) {
      return _json({ success: false, error: 'Missing content field' });
    }

    // Decode the base64 payload into a Blob (docx mime).
    const bytes = Utilities.base64Decode(base64);
    const blob = Utilities.newBlob(
      bytes,
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      filename
    );

    // Find or create the target folder.
    let folder;
    const folders = DriveApp.getFoldersByName(TARGET_FOLDER);
    if (folders.hasNext()) {
      folder = folders.next();
    } else {
      folder = DriveApp.createFolder(TARGET_FOLDER);
    }

    // Drop the raw docx into Drive first.
    const docxFile = folder.createFile(blob);

    // Convert the docx to a native Google Doc by copying with the
    // Google Docs mime type — works through the Drive REST API,
    // hit via UrlFetch with the script's own OAuth token.
    const accessToken = ScriptApp.getOAuthToken();
    const convertResp = UrlFetchApp.fetch(
      'https://www.googleapis.com/drive/v3/files/' + docxFile.getId() + '/copy',
      {
        method: 'post',
        contentType: 'application/json',
        headers: { Authorization: 'Bearer ' + accessToken },
        payload: JSON.stringify({
          name: filename.replace(/\.docx$/i, ''),
          mimeType: 'application/vnd.google-apps.document',
          parents: [folder.getId()]
        }),
        muteHttpExceptions: true
      }
    );

    const convertResult = JSON.parse(convertResp.getContentText());
    if (!convertResult.id) {
      return _json({
        success: false,
        error: 'Conversion failed',
        details: convertResult
      });
    }

    // Optionally delete the raw .docx now that we have the Doc copy.
    DriveApp.getFileById(docxFile.getId()).setTrashed(true);

    return _json({
      success: true,
      file_id: convertResult.id,
      url: 'https://docs.google.com/document/d/' + convertResult.id + '/edit'
    });

  } catch (err) {
    return _json({ success: false, error: err.toString() });
  }
}

function doGet() {
  return _json({ status: 'online', target_folder: TARGET_FOLDER });
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
