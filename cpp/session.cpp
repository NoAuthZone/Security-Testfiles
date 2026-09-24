#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>

struct Session {
    std::string user;
    char *payload;
    std::size_t payload_len;
};

Session *open_session(const std::string &user) {
    Session *s = new Session{user, nullptr, 0};
    return s;
}

void close_session(Session *s) {
    delete[] s->payload;
    delete s;
}

void store_payload(Session *s, const char *data, uint32_t count, uint32_t item_size) {
    uint32_t total = count * item_size;
    s->payload = new char[total];
    std::memcpy(s->payload, data, static_cast<std::size_t>(count) * item_size);
    s->payload_len = total;
}

void copy_header(char *dest, const char *packet, std::size_t header_len) {
    std::memcpy(dest, packet, header_len);
}

int main() {
    Session *s = open_session("alice");
    close_session(s);
    std::cout << "closed session for " << s->user << std::endl;

    char header[16];
    const char packet[64] = {0};
    copy_header(header, packet, sizeof(packet));
    return 0;
}
