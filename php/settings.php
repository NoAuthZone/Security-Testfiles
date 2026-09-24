<?php
$pdo = new PDO("mysql:host=localhost;dbname=app", "app", getenv("DB_PASSWORD"), [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$action = $_GET["action"] ?? "view";
$pages = ["about" => "pages/about.php", "help" => "pages/help.php"];

function e(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES, "UTF-8");
}

if ($action === "view") {
    $stmt = $pdo->prepare("SELECT name, bio FROM users WHERE id = ?");
    $stmt->execute([(int) ($_GET["id"] ?? 0)]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC) ?: ["name" => "", "bio" => ""];
    echo "<h1>Settings of " . e($user["name"]) . "</h1>";
    echo "<p>" . e($user["bio"]) . "</p>";
}

if ($action === "prefs" && isset($_COOKIE["prefs"])) {
    $prefs = json_decode($_COOKIE["prefs"], true);
    $theme = is_array($prefs) && is_string($prefs["theme"] ?? null) ? $prefs["theme"] : "default";
    echo "Theme: " . e($theme);
}

if ($action === "page") {
    $key = $_GET["page"] ?? "";
    if (isset($pages[$key])) {
        include $pages[$key];
    }
}
