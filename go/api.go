package main

import (
	"database/sql"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os/exec"
	"regexp"
)

var store *sql.DB

var fileNameRe = regexp.MustCompile(`^[a-zA-Z0-9_-]{1,64}\.(jpg|png)$`)

var allowedHosts = map[string]bool{"images.example.com": true, "cdn.example.com": true}

var noRedirectClient = &http.Client{
	CheckRedirect: func(req *http.Request, via []*http.Request) error {
		return http.ErrUseLastResponse
	},
}

func customerHandler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	rows, err := store.Query("SELECT id, email FROM customers WHERE name = $1", name)
	if err != nil {
		http.Error(w, "query failed", http.StatusInternalServerError)
		return
	}
	defer rows.Close()
	fmt.Fprintln(w, "ok")
}

func thumbnailHandler(w http.ResponseWriter, r *http.Request) {
	file := r.URL.Query().Get("file")
	if !fileNameRe.MatchString(file) {
		http.Error(w, "invalid file", http.StatusBadRequest)
		return
	}
	out, err := exec.Command("convert", "/uploads/"+file, "-thumbnail", "128x128", "/tmp/thumb.png").CombinedOutput()
	if err != nil {
		http.Error(w, string(out), http.StatusInternalServerError)
		return
	}
	w.Write([]byte("done"))
}

func imageProxyHandler(w http.ResponseWriter, r *http.Request) {
	u, err := url.Parse(r.URL.Query().Get("url"))
	if err != nil || u.Scheme != "https" || !allowedHosts[u.Hostname()] {
		http.Error(w, "host not allowed", http.StatusBadRequest)
		return
	}
	resp, err := noRedirectClient.Get(u.String())
	if err != nil {
		http.Error(w, "fetch failed", http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()
	io.Copy(w, io.LimitReader(resp.Body, 1<<20))
}

func main() {
	http.HandleFunc("/customer", customerHandler)
	http.HandleFunc("/thumbnail", thumbnailHandler)
	http.HandleFunc("/image", imageProxyHandler)
	http.ListenAndServe(":8081", nil)
}
