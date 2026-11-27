// Host regression test (no console needed):
// g++ -std=c++17 -o /tmp/language_test tests/language_test.cpp Language.cpp Controls.cpp Layout.cpp RomInfo.cpp ../ScreenLayout.cpp && /tmp/language_test
#include <stdio.h>
#include <string.h>
#include <vector>

#include "../Language.h"
#include "../Controls.h"
#include "../Layout.h"
#include "../RomInfo.h"

static int Fails = 0;
#define CHECK(c) do { if (!(c)) { printf("FAIL line %d: %s\n", __LINE__, #c); Fails++; } } while (0)

int main()
{
    using namespace I18n;
    CHECK(GetLanguage() == Language::French);
    CHECK(ParseLanguage("") == Language::French);
    CHECK(ParseLanguage("unsupported") == Language::French);
    CHECK(ParseLanguage("fr") == Language::French);
    CHECK(ParseLanguage("en") == Language::English);
    CHECK(strcmp(Tr("Réglages"), "Réglages") == 0);
    CHECK(strcmp(LanguageCode(), "fr") == 0 && BannerLanguage() == 2);

    // Construct profiles before switching: their stored names must remain stable.
    auto profiles = BuiltinProfiles();
    std::string stored = profiles[1].Write();
    SetLanguage(ParseLanguage("en"));
    CHECK(strcmp(LanguageCode(), "en") == 0 && BannerLanguage() == 1);
    CHECK(strcmp(Tr("Langue"), "Language") == 0);
    CHECK(strcmp(Tr("Réglages"), "Settings") == 0);
    CHECK(strcmp(Tr("Charger l'état "), "Load state ") == 0);
    CHECK(strcmp(Tr("Pour jouer, copiez vos propres jeux (fichiers .nds) sur la carte SD, par exemple dans le dossier sdmc:/roms/nds. "
                    "Honeydew ne contient aucun jeu et n'en fournit pas."),
                 "To play, copy your own games (.nds files) to the SD card, for example to sdmc:/roms/nds. Honeydew does not include or provide any games.") == 0);
    // Button glyphs, whitespace and concatenated labels must survive translation.
    CHECK(strcmp(Tr("\uE0E0 Choisir"), "\uE0E0 Choose") == 0);
    CHECK(strcmp(Tr("\uE0E0 Valider   \uE0ED\uE0EE Changer   \uE0E1 Reprendre"),
                 "\uE0E0 Confirm   \uE0ED\uE0EE Change   \uE0E1 Resume") == 0);
    CHECK(strcmp(Tr("not a translation key"), "not a translation key") == 0);
    CHECK(strcmp(Tr(""), "") == 0);
    CHECK(strcmp(LayoutName(0), "vertical") == 0);
    CHECK(strcmp(SizingName(4), "bottom only") == 0);
    CHECK(strcmp(RotationName(1), "book (90°)") == 0);
    CHECK(strcmp(DsKeyName(DsUp), "Up") == 0);
    CHECK(strcmp(SwButtonName(-1), "none") == 0);
    CHECK(strcmp(RightStickName(RightAim), "aiming (drag)") == 0);
    CHECK(ProfileDisplayName(profiles[1]) == "Aiming (Metroid)");
    CHECK(profiles[1].Write() == stored);
    ControlProfile custom = profiles[1];
    custom.Id = "custom1";
    CHECK(ProfileDisplayName(custom) == "Visée (Metroid)");
    custom = profiles[1];
    custom.Name = "My own profile";
    CHECK(ProfileDisplayName(custom) == "My own profile");

    // Banner selection follows the app language; English remains the fallback for an empty French title.
    std::vector<uint8_t> banner(0x840, 0);
    auto title = [&](int lang, const char* text) {
        for (size_t i = 0; text[i]; i++) banner[0x240 + 0x100 * lang + 2 * i] = text[i];
    };
    title(1, "English title");
    title(2, "Titre francais");
    RomInfo info;
    ParseBanner(banner.data(), banner.size(), info, BannerLanguage());
    CHECK(info.Title == "English title");
    SetLanguage(ParseLanguage("fr"));
    ParseBanner(banner.data(), banner.size(), info, BannerLanguage());
    CHECK(info.Title == "Titre francais");
    CHECK(strcmp(Tr("Langue"), "Langue") == 0);
    CHECK(strcmp(LayoutName(0), "verticale") == 0);
    CHECK(strcmp(DsKeyName(DsUp), "Haut") == 0);
    CHECK(ProfileDisplayName(profiles[1]) == "Visée (Metroid)");
    memset(banner.data() + 0x440, 0, 0x100);
    ParseBanner(banner.data(), banner.size(), info, BannerLanguage());
    CHECK(info.Title == "English title");

    printf(Fails ? "%d FAILURES\n" : "all language tests passed\n", Fails);
    return Fails != 0;
}
