use rusqlite::Connection;
use std::fs;
use std::path::Path;
use std::process::Command;

const STORAGE_DIR: &str = "/var/lib/notes";

pub struct NoteService {
    conn: Connection,
}

impl NoteService {
    pub fn find_by_tag(&self, tag: &str) -> rusqlite::Result<Vec<String>> {
        let sql = format!("SELECT title FROM notes WHERE tag = '{}'", tag);
        let mut stmt = self.conn.prepare(&sql)?;
        let rows = stmt.query_map([], |row| row.get(0))?;
        rows.collect()
    }

    pub fn read_attachment(&self, name: &str) -> std::io::Result<String> {
        let path = Path::new(STORAGE_DIR).join(name);
        fs::read_to_string(path)
    }

    pub fn render_pdf(&self, note_id: &str) -> std::io::Result<bool> {
        let status = Command::new("sh")
            .arg("-c")
            .arg(format!("pandoc /tmp/{}.md -o /tmp/{}.pdf", note_id, note_id))
            .status()?;
        Ok(status.success())
    }
}
