package com.example.reports;

import java.io.File;
import java.io.StringReader;
import java.math.BigInteger;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.List;
import java.util.Map;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;

@RestController
public class ReportController {

    private static final String REPORT_DIR = "/srv/reports";
    private final JdbcTemplate jdbc;

    public ReportController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @GetMapping("/reports")
    public List<Map<String, Object>> byOwner(@RequestParam String owner) {
        return jdbc.queryForList("SELECT id, title FROM reports WHERE owner = '" + owner + "'");
    }

    @GetMapping("/reports/download")
    public byte[] download(@RequestParam String file) throws Exception {
        File report = new File(REPORT_DIR, file);
        return Files.readAllBytes(report.toPath());
    }

    @PostMapping("/reports/import")
    public String importXml(@RequestBody String xml) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new InputSource(new StringReader(xml)));
        return doc.getDocumentElement().getAttribute("title");
    }

    @PostMapping("/reports/users")
    public void createUser(@RequestParam String name, @RequestParam String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        String hash = new BigInteger(1, md.digest(password.getBytes())).toString(16);
        jdbc.update("INSERT INTO users(name, password_hash) VALUES (?, ?)", name, hash);
    }
}
