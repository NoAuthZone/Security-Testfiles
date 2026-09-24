use rusqlite::{params, Connection};
use std::fs;
use std::io::{Error, ErrorKind};
use std::path::{Component, Path};
use std::process::Command;

const STORAGE_DIR: &str = "/var/lib/docs";

pub struct DocumentStore {
    conn: Connection,
}

fn is_plain_name(name: &str) -> bool {
    let path = Path::new(name);
    path.components().count() == 1
        && matches!(path.components().next(), Some(Component::Normal(_)))
}

impl DocumentStore {
    pub fn find_by_owner(&self, owner: &str) -> rusqlite::Result<Vec<String>> {
        let mut stmt = self.conn.prepare("SELECT title FROM docs WHERE owner = ?1")?;
        let rows = stmt.query_map(params![owner], |row| row.get(0))?;
        rows.collect()
    }

    pub fn read_file(&self, name: &str) -> std::io::Result<String> {
        if !is_plain_name(name) {
            return Err(Error::new(ErrorKind::InvalidInput, "invalid file name"));
        }
        fs::read_to_string(Path::new(STORAGE_DIR).join(name))
    }

    pub fn export(&self, doc_id: u64) -> std::io::Result<bool> {
        let input = format!("/tmp/{}.md", doc_id);
        let output = format!("/tmp/{}.pdf", doc_id);
        let status = Command::new("pandoc").args([&input, "-o", &output]).status()?;
        Ok(status.success())
    }
}
