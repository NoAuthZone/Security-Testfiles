#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <string>
#include <vector>

struct Entry {
    std::string key;
    std::vector<char> data;
};

std::unique_ptr<Entry> make_entry(const std::string &key) {
    return std::make_unique<Entry>(Entry{key, {}});
}

bool store_data(Entry &e, const std::vector<char> &input, std::size_t count, std::size_t item_size) {
    if (item_size != 0 && count > std::numeric_limits<std::size_t>::max() / item_size) {
        return false;
    }
    std::size_t total = count * item_size;
    if (total > input.size()) {
        return false;
    }
    e.data.assign(input.begin(), input.begin() + static_cast<std::ptrdiff_t>(total));
    return true;
}

std::optional<std::string> read_header(const std::vector<char> &packet, std::size_t header_len) {
    if (header_len > packet.size()) {
        return std::nullopt;
    }
    return std::string(packet.begin(), packet.begin() + static_cast<std::ptrdiff_t>(header_len));
}

int main() {
    auto entry = make_entry("config");
    std::vector<char> input(64, 'x');
    if (store_data(*entry, input, 8, 8)) {
        std::cout << "stored " << entry->data.size() << " bytes for " << entry->key << std::endl;
    }
    if (auto header = read_header(input, 16)) {
        std::cout << "header length " << header->size() << std::endl;
    }
    return 0;
}
