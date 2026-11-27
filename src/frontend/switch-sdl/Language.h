/*
    Copyright 2016-2026 melonDS team

    This file is part of melonDS.

    melonDS is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    melonDS is distributed in the hope that it will be useful, but WITHOUT ANY
    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with melonDS. If not, see http://www.gnu.org/licenses/.
*/

#ifndef SWITCH_LANGUAGE_H
#define SWITCH_LANGUAGE_H

#include <string>

namespace I18n
{
enum class Language { French, English };

// Missing/unsupported codes preserve the original French UI.
Language ParseLanguage(const std::string& code);
void SetLanguage(Language language);
Language GetLanguage();
const char* LanguageCode();
int BannerLanguage(); // DS banner: 1 English, 2 French. Does not change DS firmware.
const char* Tr(const char* french);
}

#endif
