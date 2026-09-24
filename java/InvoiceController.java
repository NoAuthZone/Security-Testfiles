package com.example.invoices;

import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;

@RestController
public class InvoiceController {

    private static final Path INVOICE_DIR = Path.of("/srv/invoices").toAbsolutePath().normalize();
    private final JdbcTemplate jdbc;
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    public InvoiceController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @GetMapping("/invoices")
    public List<Map<String, Object>> byCustomer(@RequestParam String customer) {
        return jdbc.queryForList("SELECT id, amount FROM invoices WHERE customer = ?", customer);
    }

    @GetMapping("/invoices/download")
    public byte[] download(@RequestParam String file) throws Exception {
        Path target = INVOICE_DIR.resolve(file).normalize();
        if (!target.startsWith(INVOICE_DIR)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
        }
        return Files.readAllBytes(target);
    }

    @PostMapping("/invoices/import")
    public String importXml(@RequestBody String xml) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
        Document doc = factory.newDocumentBuilder().parse(new InputSource(new StringReader(xml)));
        return doc.getDocumentElement().getAttribute("number");
    }

    @PostMapping("/invoices/users")
    public void createUser(@RequestParam String name, @RequestParam String password) {
        jdbc.update("INSERT INTO users(name, password_hash) VALUES (?, ?)", name, encoder.encode(password));
    }
}
