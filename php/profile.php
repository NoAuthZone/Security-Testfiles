<?php
$db = new mysqli("localhost", "app", getenv("DB_PASSWORD"), "app");

$action = $_GET["action"] ?? "view";

if ($action === "view") {
    $id = $_GET["id"];
    $result = $db->query("SELECT name, bio FROM users WHERE id = " . $id);
    $user = $result->fetch_assoc();
    echo "<h1>Profile of " . $_GET["name"] . "</h1>";
    echo "<p>" . htmlspecialchars($user["bio"] ?? "", ENT_QUOTES, "UTF-8") . "</p>";
}

if ($action === "prefs" && isset($_COOKIE["prefs"])) {
    $prefs = unserialize($_COOKIE["prefs"]);
    echo "Theme: " . htmlspecialchars($prefs["theme"] ?? "default", ENT_QUOTES, "UTF-8");
}

if ($action === "page") {
    include "pages/" . $_GET["page"];
}
