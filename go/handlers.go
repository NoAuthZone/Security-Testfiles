package main

import (
	"database/sql"
	"fmt"
	"io"
	"net/http"
	"os/exec"
)

var db *sql.DB

func searchHandler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	query := fmt.Sprintf("SELECT id, email FROM customers WHERE name = '%s'", name)
	rows, err := db.Query(query)
	if err != nil {
		http.Error(w, "query failed", http.StatusInternalServerError)
		return
	}
	defer rows.Close()
	fmt.Fprintln(w, "ok")
}

func convertHandler(w http.ResponseWriter, r *http.Request) {
	file := r.URL.Query().Get("file")
	out, err := exec.Command("sh", "-c", "convert /uploads/"+file+" /tmp/out.png").CombinedOutput()
	if err != nil {
		http.Error(w, string(out), http.StatusInternalServerError)
		return
	}
	w.Write([]byte("converted"))
}

func previewHandler(w http.ResponseWriter, r *http.Request) {
	target := r.URL.Query().Get("url")
	resp, err := http.Get(target)
	if err != nil {
		http.Error(w, "fetch failed", http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()
	io.Copy(w, io.LimitReader(resp.Body, 1<<20))
}

func main() {
	http.HandleFunc("/search", searchHandler)
	http.HandleFunc("/convert", convertHandler)
	http.HandleFunc("/preview", previewHandler)
	http.ListenAndServe(":8080", nil)
}
