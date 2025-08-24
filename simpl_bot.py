#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تيليجرام لبيع البروكسيات
Simple Proxy Bot - Telegram Bot for Selling Proxies
"""

import os
import asyncio
import logging
import sqlite3
import json
import random
import string
import pandas as pd
import io
import csv
import openpyxl
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

# تكوين اللوجينج
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# الإعدادات الثابتة
ADMIN_PASSWORD = "sohilSOHIL"
TOKEN = "8408804784:AAG8cSTsDQfycDaXOX9YMmc_OB3wABez7LA"
DATABASE_FILE = "proxy_bot.db"
ADMIN_CHAT_ID = None  # سيتم تحديده عند أول تسجيل دخول للأدمن

# حالات المحادثة
(
    ADMIN_LOGIN, ADMIN_MENU, PROCESS_ORDER, 
    ENTER_PROXY_TYPE, ENTER_PROXY_ADDRESS, ENTER_PROXY_PORT,
    ENTER_COUNTRY, ENTER_STATE, ENTER_USERNAME, ENTER_PASSWORD,
    ENTER_THANK_MESSAGE, PAYMENT_PROOF, CUSTOM_MESSAGE,
    REFERRAL_AMOUNT, USER_LOOKUP, QUIET_HOURS, LANGUAGE_SELECTION,
    PAYMENT_METHOD_SELECTION, WITHDRAWAL_REQUEST, SET_PRICE_STATIC,
    SET_PRICE_SOCKS, ADMIN_ORDER_INQUIRY, BROADCAST_MESSAGE,
    BROADCAST_USERS, BROADCAST_CONFIRM
) = range(25)

# قواميس البيانات
STATIC_COUNTRIES = {
    'ar': {
        'DE': '🇩🇪 ألمانيا',
        'US': '🇺🇸 أميركا',
        'UK': '🇬🇧 بريطانيا',
        'FR': '🇫🇷 فرنسا'
    },
    'en': {
        'FR': '🇫🇷 France',
        'DE': '🇩🇪 Germany',
        'UK': '🇬🇧 United Kingdom',
        'US': '🇺🇸 United States'
    }
}

SOCKS_COUNTRIES = {
    'ar': {
        'US': '🇺🇸 أميركا',
        'UK': '🇬🇧 بريطانيا',
        'DE': '🇩🇪 ألمانيا',
        'FR': '🇫🇷 فرنسا',
        'CA': '🇨🇦 كندا',
        'AU': '🇦🇺 أستراليا',
        'AT': '🇦🇹 النمسا',
        'AL': '🇦🇱 ألبانيا',
        'UA': '🇺🇦 أوكرانيا',
        'IE': '🇮🇪 أيرلندا',
        'IS': '🇮🇸 أيسلندا',
        'EE': '🇪🇪 إستونيا',
        'ES': '🇪🇸 إسبانيا',
        'IT': '🇮🇹 إيطاليا',
        'AE': '🇦🇪 الإمارات العربية المتحدة',
        'BA': '🇧🇦 البوسنة والهرسك',
        'PT': '🇵🇹 البرتغال',
        'BG': '🇧🇬 بلغاريا',
        'BE': '🇧🇪 بلجيكا',
        'BY': '🇧🇾 بيلاروسيا',
        'CZ': '🇨🇿 التشيك',
        'DK': '🇩🇰 الدنمارك',
        'SE': '🇸🇪 السويد',
        'CH': '🇨🇭 سويسرا',
        'RS': '🇷🇸 صربيا',
        'SY': '🇸🇾 سوريا',
        'SK': '🇸🇰 سلوفاكيا',
        'FI': '🇫🇮 فنلندا',
        'CY': '🇨🇾 قبرص',
        'LU': '🇱🇺 لوكسمبورغ',
        'LT': '🇱🇹 ليتوانيا',
        'HU': '🇭🇺 المجر',
        'MK': '🇲🇰 مقدونيا الشمالية',
        'MD': '🇲🇩 مولدوفا',
        'MT': '🇲🇹 مالطا',
        'NO': '🇳🇴 النرويج',
        'NL': '🇳🇱 هولندا',
        'GR': '🇬🇷 اليونان',
        'PL': '🇵🇱 بولندا',
        'RO': '🇷🇴 رومانيا',
        'LV': '🇱🇻 لاتفيا',
        'SI': '🇸🇮 سلوفينيا',
        'HR': '🇭🇷 كرواتيا',
        'TR': '🇹🇷 تركيا',
        'RU': '🇷🇺 روسيا',
        'JP': '🇯🇵 اليابان',
        'KR': '🇰🇷 كوريا الجنوبية',
        'SG': '🇸🇬 سنغافورة',
        'MY': '🇲🇾 ماليزيا',
        'TH': '🇹🇭 تايلاند',
        'VN': '🇻🇳 فيتنام',
        'IN': '🇮🇳 الهند',
        'BR': '🇧🇷 البرازيل',
        'MX': '🇲🇽 المكسيك',
        'AR': '🇦🇷 الأرجنتين',
        'CL': '🇨🇱 تشيلي',
        'CO': '🇨🇴 كولومبيا',
        'ZA': '🇿🇦 جنوب أفريقيا',
        'EG': '🇪🇬 مصر',
        'SA': '🇸🇦 السعودية',
        'IL': '🇮🇱 إسرائيل',
        'NZ': '🇳🇿 نيوزيلندا'
    },
    'en': {
        'US': '🇺🇸 United States',
        'UK': '🇬🇧 United Kingdom',
        'DE': '🇩🇪 Germany',
        'FR': '🇫🇷 France',
        'CA': '🇨🇦 Canada',
        'AU': '🇦🇺 Australia',
        'AT': '🇦🇹 Austria',
        'AL': '🇦🇱 Albania',
        'UA': '🇺🇦 Ukraine',
        'IE': '🇮🇪 Ireland',
        'IS': '🇮🇸 Iceland',
        'EE': '🇪🇪 Estonia',
        'ES': '🇪🇸 Spain',
        'IT': '🇮🇹 Italy',
        'AE': '🇦🇪 United Arab Emirates',
        'BA': '🇧🇦 Bosnia and Herzegovina',
        'PT': '🇵🇹 Portugal',
        'BG': '🇧🇬 Bulgaria',
        'BE': '🇧🇪 Belgium',
        'BY': '🇧🇾 Belarus',
        'CZ': '🇨🇿 Czech Republic',
        'DK': '🇩🇰 Denmark',
        'SE': '🇸🇪 Sweden',
        'CH': '🇨🇭 Switzerland',
        'RS': '🇷🇸 Serbia',
        'SY': '🇸🇾 Syria',
        'SK': '🇸🇰 Slovakia',
        'FI': '🇫🇮 Finland',
        'CY': '🇨🇾 Cyprus',
        'LU': '🇱🇺 Luxembourg',
        'LT': '🇱🇹 Lithuania',
        'HU': '🇭🇺 Hungary',
        'MK': '🇲🇰 North Macedonia',
        'MD': '🇲🇩 Moldova',
        'MT': '🇲🇹 Malta',
        'NO': '🇳🇴 Norway',
        'NL': '🇳🇱 Netherlands',
        'GR': '🇬🇷 Greece',
        'PL': '🇵🇱 Poland',
        'RO': '🇷🇴 Romania',
        'LV': '🇱🇻 Latvia',
        'SI': '🇸🇮 Slovenia',
        'HR': '🇭🇷 Croatia',
        'TR': '🇹🇷 Turkey',
        'RU': '🇷🇺 Russia',
        'JP': '🇯🇵 Japan',
        'KR': '🇰🇷 South Korea',
        'SG': '🇸🇬 Singapore',
        'MY': '🇲🇾 Malaysia',
        'TH': '🇹🇭 Thailand',
        'VN': '🇻🇳 Vietnam',
        'IN': '🇮🇳 India',
        'BR': '🇧🇷 Brazil',
        'MX': '🇲🇽 Mexico',
        'AR': '🇦🇷 Argentina',
        'CL': '🇨🇱 Chile',
        'CO': '🇨🇴 Colombia',
        'ZA': '🇿🇦 South Africa',
        'EG': '🇪🇬 Egypt',
        'SA': '🇸🇦 Saudi Arabia',
        'IL': '🇮🇱 Israel',
        'NZ': '🇳🇿 New Zealand'
    }
}

US_STATES = {
    'ar': {
        'AL': 'ألاباما',
        'AK': 'ألاسكا', 
        'AZ': 'أريزونا',
        'AR': 'أركنساس',
        'CA': 'كاليفورنيا',
        'CO': 'كولورادو',
        'CT': 'كونيتيكت',
        'DE': 'ديلاوير',
        'FL': 'فلوريدا',
        'GA': 'جورجيا',
        'HI': 'هاواي',
        'ID': 'أيداهو',
        'IL': 'إلينوي',
        'IN': 'إنديانا',
        'IA': 'أيوا',
        'KS': 'كانساس',
        'KY': 'كنتاكي',
        'LA': 'لويزيانا',
        'ME': 'مين',
        'MD': 'ماريلاند',
        'MA': 'ماساتشوستس',
        'MI': 'ميشيغان',
        'MN': 'مينيسوتا',
        'MS': 'ميسيسيبي',
        'MO': 'ميزوري',
        'MT': 'مونتانا',
        'NE': 'نبراسكا',
        'NV': 'نيفادا',
        'NH': 'نيو هامبشير',
        'NJ': 'نيو جيرسي',
        'NM': 'نيو مكسيكو',
        'NY': 'نيويورك',
        'NC': 'كارولينا الشمالية',
        'ND': 'داكوتا الشمالية',
        'OH': 'أوهايو',
        'OK': 'أوكلاهوما',
        'OR': 'أوريغون',
        'PA': 'بنسلفانيا',
        'RI': 'رود آيلاند',
        'SC': 'كارولينا الجنوبية',
        'SD': 'داكوتا الجنوبية',
        'TN': 'تينيسي',
        'TX': 'تكساس',
        'UT': 'يوتا',
        'VT': 'فيرمونت',
        'VA': 'فيرجينيا',
        'WA': 'واشنطن',
        'WV': 'فيرجينيا الغربية',
        'WI': 'ويسكونسن',
        'WY': 'وايومنغ'
    },
    'en': {
        'AL': 'Alabama',
        'AK': 'Alaska',
        'AZ': 'Arizona',
        'AR': 'Arkansas',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'IA': 'Iowa',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'ME': 'Maine',
        'MD': 'Maryland',
        'MA': 'Massachusetts',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MS': 'Mississippi',
        'MO': 'Missouri',
        'MT': 'Montana',
        'NE': 'Nebraska',
        'NV': 'Nevada',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NY': 'New York',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VT': 'Vermont',
        'VA': 'Virginia',
        'WA': 'Washington',
        'WV': 'West Virginia',
        'WI': 'Wisconsin',
        'WY': 'Wyoming'
    }
}

UK_STATES = {
    'ar': {
        'ENG': 'إنجلترا',
        'SCT': 'اسكتلندا',
        'WAL': 'ويلز',
        'NIR': 'أيرلندا الشمالية'
    },
    'en': {
        'ENG': 'England',
        'SCT': 'Scotland',
        'WAL': 'Wales', 
        'NIR': 'Northern Ireland'
    }
}

# مناطق ألمانيا
DE_STATES = {
    'ar': {
        'BW': 'بادن فورتمبيرغ',
        'BY': 'بافاريا',
        'BE': 'برلين',
        'BB': 'براندنبورغ',
        'HB': 'بريمن',
        'HH': 'هامبورغ',
        'HE': 'هيسن',
        'NI': 'ساكسونيا السفلى',
        'NW': 'شمال الراين وستفاليا',
        'RP': 'راينلاند بالاتينات',
        'SL': 'سارلاند',
        'SN': 'ساكسونيا',
        'ST': 'ساكسونيا أنهالت',
        'SH': 'شليسفيغ هولشتاين',
        'TH': 'تورينغن'
    },
    'en': {
        'BW': 'Baden-Württemberg',
        'BY': 'Bavaria',
        'BE': 'Berlin',
        'BB': 'Brandenburg',
        'HB': 'Bremen',
        'HH': 'Hamburg',
        'HE': 'Hesse',
        'NI': 'Lower Saxony',
        'NW': 'North Rhine-Westphalia',
        'RP': 'Rhineland-Palatinate',
        'SL': 'Saarland',
        'SN': 'Saxony',
        'ST': 'Saxony-Anhalt',
        'SH': 'Schleswig-Holstein',
        'TH': 'Thuringia'
    }
}

# مناطق فرنسا
FR_STATES = {
    'ar': {
        'ARA': 'أوفيرن رون ألب',
        'BFC': 'بورغونيا فرانش كونته',
        'BRE': 'بريتاني',
        'CVL': 'وسط وادي اللوار',
        'COR': 'كورسيكا',
        'GES': 'الألزاس الشرقي',
        'HDF': 'هو دو فرانس',
        'IDF': 'إيل دو فرانس',
        'NOR': 'نورماندي',
        'NAQ': 'آكيتين الجديدة',
        'OCC': 'أوكسيتانيا',
        'PDL': 'باي دو لا لوار',
        'PAC': 'بروفانس ألب كوت دازور'
    },
    'en': {
        'ARA': 'Auvergne-Rhône-Alpes',
        'BFC': 'Burgundy-Franche-Comté',
        'BRE': 'Brittany',
        'CVL': 'Centre-Val de Loire',
        'COR': 'Corsica',
        'GES': 'Grand Est',
        'HDF': 'Hauts-de-France',
        'IDF': 'Île-de-France',
        'NOR': 'Normandy',
        'NAQ': 'Nouvelle-Aquitaine',
        'OCC': 'Occitania',
        'PDL': 'Pays de la Loire',
        'PAC': 'Provence-Alpes-Côte d\'Azur'
    }
}

# مناطق إيطاليا
IT_STATES = {
    'ar': {
        'ABR': 'أبروتسو',
        'BAS': 'باسيليكاتا',
        'CAL': 'كالابريا',
        'CAM': 'كامبانيا',
        'EMR': 'إميليا رومانيا',
        'FVG': 'فريولي فينيتسيا جوليا',
        'LAZ': 'لاتسيو',
        'LIG': 'ليغوريا',
        'LOM': 'لومبارديا',
        'MAR': 'ماركي',
        'MOL': 'موليسي',
        'PIE': 'بيدمونت',
        'PUG': 'بوليا',
        'SAR': 'سردينيا',
        'SIC': 'صقلية',
        'TOS': 'توسكانا',
        'TRE': 'ترينتينو ألتو أديجي',
        'UMB': 'أومبريا',
        'VDA': 'وادي أوستا',
        'VEN': 'فينيتو'
    },
    'en': {
        'ABR': 'Abruzzo',
        'BAS': 'Basilicata',
        'CAL': 'Calabria',
        'CAM': 'Campania',
        'EMR': 'Emilia-Romagna',
        'FVG': 'Friuli-Venezia Giulia',
        'LAZ': 'Lazio',
        'LIG': 'Liguria',
        'LOM': 'Lombardy',
        'MAR': 'Marche',
        'MOL': 'Molise',
        'PIE': 'Piedmont',
        'PUG': 'Puglia',
        'SAR': 'Sardinia',
        'SIC': 'Sicily',
        'TOS': 'Tuscany',
        'TRE': 'Trentino-Alto Adige',
        'UMB': 'Umbria',
        'VDA': 'Aosta Valley',
        'VEN': 'Veneto'
    }
}

# مناطق إسبانيا
ES_STATES = {
    'ar': {
        'AND': 'الأندلس',
        'ARA': 'أراغون',
        'AST': 'أستورياس',
        'BAL': 'جزر البليار',
        'PV': 'الباسك',
        'CAN': 'جزر الكناري',
        'CAB': 'كانتابريا',
        'CLM': 'قشتالة لا مانتشا',
        'CYL': 'قشتالة وليون',
        'CAT': 'كاتالونيا',
        'EXT': 'إكستريمادورا',
        'GAL': 'غاليسيا',
        'MAD': 'مدريد',
        'MUR': 'مورسيا',
        'NAV': 'نافارا',
        'RIO': 'لا ريوخا',
        'VAL': 'فالنسيا'
    },
    'en': {
        'AND': 'Andalusia',
        'ARA': 'Aragon',
        'AST': 'Asturias',
        'BAL': 'Balearic Islands',
        'PV': 'Basque Country',
        'CAN': 'Canary Islands',
        'CAB': 'Cantabria',
        'CLM': 'Castile-La Mancha',
        'CYL': 'Castile and León',
        'CAT': 'Catalonia',
        'EXT': 'Extremadura',
        'GAL': 'Galicia',
        'MAD': 'Madrid',
        'MUR': 'Murcia',
        'NAV': 'Navarre',
        'RIO': 'La Rioja',
        'VAL': 'Valencia'
    }
}

# مناطق كندا
CA_STATES = {
    'ar': {
        'AB': 'ألبرتا',
        'BC': 'كولومبيا البريطانية',
        'MB': 'مانيتوبا',
        'NB': 'نيو برونزويك',
        'NL': 'نيوفاوندلاند ولابرادور',
        'NS': 'نوفا سكوتيا',
        'ON': 'أونتاريو',
        'PE': 'جزيرة الأمير إدوارد',
        'QC': 'كيبيك',
        'SK': 'ساسكاتشوان',
        'NT': 'الأقاليم الشمالية الغربية',
        'NU': 'نونافوت',
        'YT': 'يوكون'
    },
    'en': {
        'AB': 'Alberta',
        'BC': 'British Columbia',
        'MB': 'Manitoba',
        'NB': 'New Brunswick',
        'NL': 'Newfoundland and Labrador',
        'NS': 'Nova Scotia',
        'ON': 'Ontario',
        'PE': 'Prince Edward Island',
        'QC': 'Quebec',
        'SK': 'Saskatchewan',
        'NT': 'Northwest Territories',
        'NU': 'Nunavut',
        'YT': 'Yukon'
    }
}

# ولايات أستراليا
AU_STATES = {
    'ar': {
        'NSW': 'نيو ساوث ويلز',
        'VIC': 'فيكتوريا',
        'QLD': 'كوينزلاند',
        'SA': 'جنوب أستراليا',
        'WA': 'غرب أستراليا',
        'TAS': 'تاسمانيا',
        'NT': 'الإقليم الشمالي',
        'ACT': 'إقليم العاصمة الأسترالية'
    },
    'en': {
        'NSW': 'New South Wales',
        'VIC': 'Victoria',
        'QLD': 'Queensland',
        'SA': 'South Australia',
        'WA': 'Western Australia',
        'TAS': 'Tasmania',
        'NT': 'Northern Territory',
        'ACT': 'Australian Capital Territory'
    }
}

# ولايات النمسا
AT_STATES = {
    'ar': {
        'WIEN': 'فيينا',
        'NOE': 'النمسا السفلى',
        'OOE': 'النمسا العليا',
        'STMK': 'شتايرمارك',
        'KTN': 'كارينثيا',
        'SBG': 'سالزبورغ',
        'TIROL': 'تيرول',
        'VBG': 'فورآرلبرغ',
        'BGLD': 'بورغنلاند'
    },
    'en': {
        'WIEN': 'Vienna',
        'NOE': 'Lower Austria',
        'OOE': 'Upper Austria',
        'STMK': 'Styria',
        'KTN': 'Carinthia',
        'SBG': 'Salzburg',
        'TIROL': 'Tyrol',
        'VBG': 'Vorarlberg',
        'BGLD': 'Burgenland'
    }
}

# مناطق إيطاليا
IT_STATES = {
    'ar': {
        'LAZ': 'لاتسيو (روما)',
        'LOM': 'لومبارديا (ميلان)',
        'CAM': 'كامبانيا (نابولي)',
        'SIC': 'صقلية (باليرمو)',
        'VEN': 'فينيتو (فينيسيا)',
        'PIE': 'بيدمونت (تورين)',
        'PUG': 'بوليا (باري)',
        'EMR': 'إميليا رومانيا (بولونيا)',
        'TOS': 'توسكانا (فلورنسا)',
        'CAL': 'كالابريا',
        'SAR': 'سردينيا',
        'LIG': 'ليغوريا (جنوة)',
        'MAR': 'ماركي',
        'ABR': 'أبروتسو',
        'FVG': 'فريولي فينيتسيا جوليا',
        'TRE': 'ترينتينو ألتو أديجي',
        'UMB': 'أومبريا',
        'BAS': 'باسيليكاتا',
        'MOL': 'موليزي',
        'VAL': 'فالي داوستا'
    },
    'en': {
        'LAZ': 'Lazio (Rome)',
        'LOM': 'Lombardy (Milan)',
        'CAM': 'Campania (Naples)',
        'SIC': 'Sicily (Palermo)',
        'VEN': 'Veneto (Venice)',
        'PIE': 'Piedmont (Turin)',
        'PUG': 'Apulia (Bari)',
        'EMR': 'Emilia-Romagna (Bologna)',
        'TOS': 'Tuscany (Florence)',
        'CAL': 'Calabria',
        'SAR': 'Sardinia',
        'LIG': 'Liguria (Genoa)',
        'MAR': 'Marche',
        'ABR': 'Abruzzo',
        'FVG': 'Friuli-Venezia Giulia',
        'TRE': 'Trentino-Alto Adige',
        'UMB': 'Umbria',
        'BAS': 'Basilicata',
        'MOL': 'Molise',
        'VAL': 'Aosta Valley'
    }
}

# مقاطعات إسبانيا
ES_STATES = {
    'ar': {
        'MAD': 'مدريد',
        'CAT': 'كاتالونيا (برشلونة)',
        'AND': 'أندلسيا (إشبيلية)',
        'VAL': 'فالنسيا',
        'GAL': 'جاليسيا',
        'CAS': 'قشتالة وليون',
        'EUS': 'إقليم الباسك (بيلباو)',
        'CAN': 'جزر الكناري',
        'CLM': 'قشتالة لا مانشا',
        'MUR': 'مورسيا',
        'ARA': 'أراغون',
        'EXT': 'إكستريمادورا',
        'AST': 'أستورياس',
        'NAV': 'نافارا',
        'CAN_': 'كانتابريا',
        'BAL': 'جزر البليار',
        'RIO': 'لا ريوخا',
        'CEU': 'سبتة',
        'MEL': 'مليلية'
    },
    'en': {
        'MAD': 'Madrid',
        'CAT': 'Catalonia (Barcelona)',
        'AND': 'Andalusia (Seville)',
        'VAL': 'Valencia',
        'GAL': 'Galicia',
        'CAS': 'Castile and León',
        'EUS': 'Basque Country (Bilbao)',
        'CAN': 'Canary Islands',
        'CLM': 'Castilla-La Mancha',
        'MUR': 'Murcia',
        'ARA': 'Aragon',
        'EXT': 'Extremadura',
        'AST': 'Asturias',
        'NAV': 'Navarre',
        'CAN_': 'Cantabria',
        'BAL': 'Balearic Islands',
        'RIO': 'La Rioja',
        'CEU': 'Ceuta',
        'MEL': 'Melilla'
    }
}

# مقاطعات هولندا
NL_STATES = {
    'ar': {
        'NH': 'شمال هولندا (أمستردام)',
        'ZH': 'جنوب هولندا (لاهاي)',
        'NB': 'شمال برابانت',
        'UT': 'أوترخت',
        'GE': 'خيلدرلاند',
        'OV': 'أوفريجسل',
        'LI': 'ليمبورغ',
        'FR': 'فريزلاند',
        'GR': 'خرونينغن',
        'DR': 'درينت',
        'FL': 'فليفولاند',
        'ZE': 'زيلاند'
    },
    'en': {
        'NH': 'North Holland (Amsterdam)',
        'ZH': 'South Holland (The Hague)',
        'NB': 'North Brabant',
        'UT': 'Utrecht',
        'GE': 'Gelderland',
        'OV': 'Overijssel',
        'LI': 'Limburg',
        'FR': 'Friesland',
        'GR': 'Groningen',
        'DR': 'Drenthe',
        'FL': 'Flevoland',
        'ZE': 'Zeeland'
    }
}

# مقاطعات بلجيكا
BE_STATES = {
    'ar': {
        'BRU': 'بروكسل العاصمة',
        'VLG': 'فلاندرز',
        'WAL': 'والونيا',
        'ANT': 'أنتويرب',
        'LIM': 'ليمبورغ',
        'OVL': 'فلاندرز الشرقية',
        'WVL': 'فلاندرز الغربية',
        'VBR': 'فلامس برابانت',
        'HAI': 'هينو',
        'LIE': 'لييج',
        'LUX': 'لوكسمبورغ البلجيكية',
        'NAM': 'نامور',
        'WBR': 'والون برابانت'
    },
    'en': {
        'BRU': 'Brussels Capital',
        'VLG': 'Flanders',
        'WAL': 'Wallonia',
        'ANT': 'Antwerp',
        'LIM': 'Limburg',
        'OVL': 'East Flanders',
        'WVL': 'West Flanders',
        'VBR': 'Flemish Brabant',
        'HAI': 'Hainaut',
        'LIE': 'Liège',
        'LUX': 'Luxembourg (Belgium)',
        'NAM': 'Namur',
        'WBR': 'Walloon Brabant'
    }
}

# أقاليم سويسرا
CH_STATES = {
    'ar': {
        'ZH': 'زيورخ',
        'BE': 'برن',
        'LU': 'لوسيرن',
        'UR': 'أوري',
        'SZ': 'شفيتس',
        'OW': 'أوبفالدن',
        'NW': 'نيدفالدن',
        'GL': 'غلاريس',
        'ZG': 'تسوغ',
        'FR': 'فريبورغ',
        'SO': 'سولوتورن',
        'BS': 'بازل المدينة',
        'BL': 'بازل الريف',
        'SH': 'شافهاوزن',
        'AR': 'أبنزل الخارجية',
        'AI': 'أبنزل الداخلية',
        'SG': 'سانت غالن',
        'GR': 'غراوبوندن',
        'AG': 'أرغاو',
        'TG': 'تورغاو',
        'TI': 'تيتشينو',
        'VD': 'فو',
        'VS': 'فاليه',
        'NE': 'نوشاتيل',
        'GE': 'جنيف',
        'JU': 'جورا'
    },
    'en': {
        'ZH': 'Zurich',
        'BE': 'Bern',
        'LU': 'Lucerne',
        'UR': 'Uri',
        'SZ': 'Schwyz',
        'OW': 'Obwalden',
        'NW': 'Nidwalden',
        'GL': 'Glarus',
        'ZG': 'Zug',
        'FR': 'Fribourg',
        'SO': 'Solothurn',
        'BS': 'Basel-Stadt',
        'BL': 'Basel-Landschaft',
        'SH': 'Schaffhausen',
        'AR': 'Appenzell Ausserrhoden',
        'AI': 'Appenzell Innerrhoden',
        'SG': 'St. Gallen',
        'GR': 'Graubünden',
        'AG': 'Aargau',
        'TG': 'Thurgau',
        'TI': 'Ticino',
        'VD': 'Vaud',
        'VS': 'Valais',
        'NE': 'Neuchâtel',
        'GE': 'Geneva',
        'JU': 'Jura'
    }
}

# ولايات روسيا (أهم المناطق)
RU_STATES = {
    'ar': {
        'MOW': 'موسكو',
        'SPE': 'سان بطرسبرغ',
        'NSO': 'نوفوسيبيرسك',
        'EKB': 'يكاترينبورغ',
        'NIZ': 'نيجني نوفغورود',
        'KZN': 'قازان',
        'CHE': 'تشيليابينسك',
        'OMS': 'أومسك',
        'SAM': 'سامارا',
        'ROS': 'روستوف على الدون',
        'UFA': 'أوفا',
        'KRA': 'كراسنويارسك',
        'PER': 'بيرم',
        'VOR': 'فورونيج',
        'VOL': 'فولغوغراد'
    },
    'en': {
        'MOW': 'Moscow',
        'SPE': 'Saint Petersburg',
        'NSO': 'Novosibirsk',
        'EKB': 'Yekaterinburg',
        'NIZ': 'Nizhny Novgorod',
        'KZN': 'Kazan',
        'CHE': 'Chelyabinsk',
        'OMS': 'Omsk',
        'SAM': 'Samara',
        'ROS': 'Rostov-on-Don',
        'UFA': 'Ufa',
        'KRA': 'Krasnoyarsk',
        'PER': 'Perm',
        'VOR': 'Voronezh',
        'VOL': 'Volgograd'
    }
}

# محافظات اليابان (أهم المناطق)
JP_STATES = {
    'ar': {
        'TOK': 'طوكيو',
        'OSA': 'أوساكا',
        'KAN': 'كاناغاوا (يوكوهاما)',
        'AIC': 'آيتشي (ناغويا)',
        'SAI': 'سايتاما',
        'CHI': 'تشيبا',
        'HYO': 'هيوغو (كوبي)',
        'HOK': 'هوكايدو (سابورو)',
        'FUK': 'فوكوكا',
        'SHI': 'شيزوكا',
        'HIR': 'هيروشيما',
        'SEN': 'سينداي',
        'KYO': 'كيوتو',
        'NII': 'نيغاتا',
        'OKI': 'أوكيناوا'
    },
    'en': {
        'TOK': 'Tokyo',
        'OSA': 'Osaka',
        'KAN': 'Kanagawa (Yokohama)',
        'AIC': 'Aichi (Nagoya)',
        'SAI': 'Saitama',
        'CHI': 'Chiba',
        'HYO': 'Hyogo (Kobe)',
        'HOK': 'Hokkaido (Sapporo)',
        'FUK': 'Fukuoka',
        'SHI': 'Shizuoka',
        'HIR': 'Hiroshima',
        'SEN': 'Sendai',
        'KYO': 'Kyoto',
        'NII': 'Niigata',
        'OKI': 'Okinawa'
    }
}

# ولايات البرازيل (أهم المناطق)
BR_STATES = {
    'ar': {
        'SP': 'ساو باولو',
        'RJ': 'ريو دي جانيرو',
        'MG': 'ميناس جيرايس',
        'BA': 'باهيا',
        'PR': 'بارانا',
        'RS': 'ريو غراندي دو سول',
        'PE': 'بيرنامبوكو',
        'CE': 'سيارا',
        'PA': 'بارا',
        'SC': 'سانتا كاتارينا',
        'GO': 'غوياس',
        'PB': 'بارايبا',
        'MA': 'مارانهاو',
        'ES': 'إسبيريتو سانتو',
        'DF': 'المقاطعة الاتحادية (برازيليا)'
    },
    'en': {
        'SP': 'São Paulo',
        'RJ': 'Rio de Janeiro',
        'MG': 'Minas Gerais',
        'BA': 'Bahia',
        'PR': 'Paraná',
        'RS': 'Rio Grande do Sul',
        'PE': 'Pernambuco',
        'CE': 'Ceará',
        'PA': 'Pará',
        'SC': 'Santa Catarina',
        'GO': 'Goiás',
        'PB': 'Paraíba',
        'MA': 'Maranhão',
        'ES': 'Espírito Santo',
        'DF': 'Federal District (Brasília)'
    }
}

# ولايات المكسيك (أهم المناطق)
MX_STATES = {
    'ar': {
        'MX': 'مكسيكو سيتي',
        'JAL': 'خاليسكو (غوادالاخارا)',
        'NL': 'نويفو ليون (مونتيري)',
        'PUE': 'بوبلا',
        'GTO': 'غواناخواتو',
        'VER': 'فيراكروز',
        'YUC': 'يوكاتان',
        'BC': 'باجا كاليفورنيا',
        'CHIH': 'تشيهواهوا',
        'SON': 'سونورا',
        'COA': 'كواهويلا',
        'TAM': 'تاماوليباس',
        'SIN': 'سينالوا',
        'OAX': 'أواكساكا',
        'QRO': 'كيريتارو'
    },
    'en': {
        'MX': 'Mexico City',
        'JAL': 'Jalisco (Guadalajara)',
        'NL': 'Nuevo León (Monterrey)',
        'PUE': 'Puebla',
        'GTO': 'Guanajuato',
        'VER': 'Veracruz',
        'YUC': 'Yucatán',
        'BC': 'Baja California',
        'CHIH': 'Chihuahua',
        'SON': 'Sonora',
        'COA': 'Coahuila',
        'TAM': 'Tamaulipas',
        'SIN': 'Sinaloa',
        'OAX': 'Oaxaca',
        'QRO': 'Querétaro'
    }
}

# ولايات الهند (أهم المناطق)
IN_STATES = {
    'ar': {
        'DL': 'دلهي',
        'MH': 'ماهاراشترا (مومباي)',
        'KA': 'كارناتاكا (بنغالور)',
        'TN': 'تاميل نادو (تشيناي)',
        'WB': 'البنغال الغربية (كولكاتا)',
        'GJ': 'غوجارات',
        'RJ': 'راجاستان',
        'UP': 'أوتار براديش',
        'TG': 'تيلانغانا (حيدر أباد)',
        'AP': 'أندرا براديش',
        'KL': 'كيرالا',
        'OR': 'أوديشا',
        'JH': 'جهارخاند',
        'AS': 'آسام',
        'PB': 'البنجاب'
    },
    'en': {
        'DL': 'Delhi',
        'MH': 'Maharashtra (Mumbai)',
        'KA': 'Karnataka (Bangalore)',
        'TN': 'Tamil Nadu (Chennai)',
        'WB': 'West Bengal (Kolkata)',
        'GJ': 'Gujarat',
        'RJ': 'Rajasthan',
        'UP': 'Uttar Pradesh',
        'TG': 'Telangana (Hyderabad)',
        'AP': 'Andhra Pradesh',
        'KL': 'Kerala',
        'OR': 'Odisha',
        'JH': 'Jharkhand',
        'AS': 'Assam',
        'PB': 'Punjab'
    }
}

# رسائل النظام
MESSAGES = {
    'ar': {
        'welcome': """🎯 مرحباً بك في بوت بيع البروكسيات

اختر الخدمة المطلوبة من الأزرار أدناه:""",
        'static_package': """📦 Static Package

🔹 الأسعار:
- Static ISP Risk0: `3$`
- Static Residential Verizon: `4$`  
- Static Residential AT&T: `6$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{}`""",
        'socks_package': """📦 Socks Package
كافة دول العالم مع ميزة اختيار الولاية والمزود للبكج

🔹 الأسعار:
- باكج 5 بروكسيات مؤقتة: `0.4$`
- باكج 10 بروكسيات مؤقتة: `0.7$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{}`""",
        'select_country': 'اختر الدولة:',
        'select_state': 'اختر الولاية:',
        'manual_input': 'إدخال يدوي',
        'payment_methods': 'اختر طريقة الدفع:',
        'send_payment_proof': 'يرجى إرسال إثبات الدفع (صورة أو نص):',
        'order_received': '✅ تم استلام طلبك بنجاح!\n\n📋 سيتم معالجة الطلب يدوياً من الأدمن بأقرب وقت.\n\n📧 ستصلك تحديثات الحالة تلقائياً.',
        'main_menu_buttons': ['🔒 طلب بروكسي ستاتيك', '📡 طلب بروكسي سوكس', '👥 إحالاتي', '📋 تذكير بطلباتي', '⚙️ الإعدادات'],
        'admin_main_buttons': ['📋 إدارة الطلبات', '💰 إدارة الأموال', '👥 الإحالات', '📢 البث', '⚙️ الإعدادات'],
        'change_password': 'تغيير كلمة المرور',
        'password_changed': 'تم تغيير كلمة المرور بنجاح ✅',
        'invalid_password': 'كلمة المرور غير صحيحة!',
        'enter_new_password': 'يرجى إدخال كلمة المرور الجديدة:',
        'withdrawal_processing': 'جاري معالجة طلب سحب رصيدك من قبل الأدمن...',
        'admin_contact': 'ستتواصل الإدارة معك قريباً لتسليمك مكافأتك.',
        'language_change_success': 'تم تغيير اللغة إلى العربية ✅\nيرجى استخدام الأمر /start لإعادة تحميل القوائم',
        'admin_panel': '🔧 لوحة الأدمن',
        'manage_orders': 'إدارة الطلبات',
        'pending_orders': 'الطلبات المعلقة',
        'admin_login_prompt': 'يرجى إدخال كلمة المرور:',
        'order_processing': '⚙️ جاري معالجة طلبك الآن من قبل الأدمن...',
        'order_success': '✅ تم إنجاز طلبك بنجاح! تم إرسال تفاصيل البروكسي إليك.',
        'order_failed': '❌ تم رفض طلبك. يرجى التحقق من إثبات الدفع والمحاولة مرة أخرى.'
    },
    'en': {
        'welcome': """🎯 Welcome to Proxy Sales Bot

Choose the required service from the buttons below:""",
        'static_package': """📦 Static Package

🔹 Prices:
- Static ISP Risk0: `3$`
- Static Residential Verizon: `4$`
- Static Residential AT&T: `6$`

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
`cc849f22d5117db0b8fe5667e6d4b758`

- Syriatel Cash:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: `{}`""",
        'socks_package': """📦 Socks Package

🔹 Prices:
- 5 Temporary Proxies Package: `0.4$`
- 10 Temporary Proxies Package: `0.7$`

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
`cc849f22d5117db0b8fe5667e6d4b758`

- Syriatel Cash:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: `{}`""",
        'select_country': 'Select Country:',
        'select_state': 'Select State:',
        'manual_input': 'Manual Input',
        'payment_methods': 'Choose payment method:',
        'send_payment_proof': 'Please send payment proof (image or text):',
        'order_received': '✅ Your order has been received successfully!\n\n📋 Admin will process it manually soon.\n\n📧 You will receive status updates automatically.',
        'main_menu_buttons': ['🔒 Request Static Proxy', '📡 Request Socks Proxy', '👥 My Referrals', '📋 Order Reminder', '⚙️ Settings'],
        'admin_main_buttons': ['📋 Manage Orders', '💰 Manage Money', '👥 Referrals', '📢 Broadcast', '⚙️ Settings'],
        'change_password': 'Change Password',
        'password_changed': 'Password changed successfully ✅',
        'invalid_password': 'Invalid password!',
        'enter_new_password': 'Please enter new password:',
        'withdrawal_processing': 'Your withdrawal request is being processed by admin...',
        'admin_contact': 'Admin will contact you soon to deliver your reward.',
        'language_change_success': 'Language changed to English ✅\nPlease use /start command to reload menus',
        'admin_panel': '🔧 Admin Panel',
        'manage_orders': 'Manage Orders',
        'pending_orders': 'Pending Orders',
        'admin_login_prompt': 'Please enter password:',
        'order_processing': '⚙️ Your order is now being processed by admin...',
        'order_success': '✅ Your order has been completed successfully! Proxy details have been sent to you.',
        'order_failed': '❌ Your order has been rejected. Please check your payment proof and try again.'
    }
}

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'ar',
                referral_balance REAL DEFAULT 0.0,
                referred_by INTEGER,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # جدول الطلبات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                proxy_type TEXT,
                country TEXT,
                state TEXT,
                payment_method TEXT,
                payment_amount REAL,
                payment_proof TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                proxy_details TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الإحالات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                amount REAL DEFAULT 0.1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # جدول المعاملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                transaction_number TEXT UNIQUE NOT NULL,
                transaction_type TEXT NOT NULL,  -- 'proxy' or 'withdrawal'
                status TEXT DEFAULT 'completed',  -- 'completed' or 'failed'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """تنفيذ استعلام قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str, referred_by: int = None):
        """إضافة مستخدم جديد"""
        query = '''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, referred_by)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (user_id, username, first_name, last_name, referred_by))
    
    def get_user(self, user_id: int) -> Optional[tuple]:
        """الحصول على بيانات المستخدم"""
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def update_user_language(self, user_id: int, language: str):
        """تحديث لغة المستخدم"""
        query = "UPDATE users SET language = ? WHERE user_id = ?"
        self.execute_query(query, (language, user_id))
    
    def create_order(self, order_id: str, user_id: int, proxy_type: str, country: str, state: str, payment_method: str):
        """إنشاء طلب جديد"""
        query = '''
            INSERT INTO orders (id, user_id, proxy_type, country, state, payment_method)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (order_id, user_id, proxy_type, country, state, payment_method))
    
    def update_order_payment_proof(self, order_id: str, payment_proof: str):
        """تحديث إثبات الدفع للطلب"""
        query = "UPDATE orders SET payment_proof = ? WHERE id = ?"
        self.execute_query(query, (payment_proof, order_id))
    
    def get_pending_orders(self) -> List[tuple]:
        """الحصول على الطلبات المعلقة"""
        query = "SELECT * FROM orders WHERE status = 'pending'"
        return self.execute_query(query)
    
    def log_action(self, user_id: int, action: str, details: str = ""):
        """تسجيل إجراء في السجل"""
        query = "INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)"
        self.execute_query(query, (user_id, action, details))

# إنشاء مدير قاعدة البيانات
db = DatabaseManager(DATABASE_FILE)

def load_saved_prices():
    """تحميل الأسعار المحفوظة من قاعدة البيانات عند بدء تشغيل البوت"""
    try:
        # تحميل أسعار الستاتيك
        static_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'static_prices'")
        if static_prices_result:
            static_prices_text = static_prices_result[0][0]
            try:
                if "," in static_prices_text:
                    price_parts = static_prices_text.split(",")
                    static_prices = {}
                    for part in price_parts:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            static_prices[key.strip()] = value.strip()
                else:
                    static_prices = {
                        "ISP": static_prices_text.strip(),
                        "Verizon": static_prices_text.strip(), 
                        "ATT": static_prices_text.strip()
                    }
                
                # تحديث رسائل الستاتيك
                update_static_messages(static_prices)
                print(f"📊 تم تحميل أسعار الستاتيك: {static_prices}")
            except Exception as e:
                print(f"خطأ في تحليل أسعار الستاتيك: {e}")
        
        # تحميل أسعار السوكس
        socks_prices_result = db.execute_query("SELECT value FROM settings WHERE key = 'socks_prices'")
        if socks_prices_result:
            socks_prices_text = socks_prices_result[0][0]
            try:
                if "," in socks_prices_text:
                    price_parts = socks_prices_text.split(",")
                    socks_prices = {}
                    for part in price_parts:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            socks_prices[key.strip()] = value.strip()
                else:
                    socks_prices = {
                        "5proxy": socks_prices_text.strip(),
                        "10proxy": str(float(socks_prices_text.strip()) * 1.75)
                    }
                
                # تحديث رسائل السوكس
                update_socks_messages(socks_prices)
                print(f"📊 تم تحميل أسعار السوكس: {socks_prices}")
            except Exception as e:
                print(f"خطأ في تحليل أسعار السوكس: {e}")
        
        # تحميل قيمة الإحالة
        referral_amount_result = db.execute_query("SELECT value FROM settings WHERE key = 'referral_amount'")
        if referral_amount_result:
            referral_amount = float(referral_amount_result[0][0])
            print(f"💰 تم تحميل قيمة الإحالة: {referral_amount}$")
        
    except Exception as e:
        print(f"خطأ في تحميل الأسعار المحفوظة: {e}")

def update_static_messages(static_prices):
    """تحديث رسائل البروكسي الستاتيك"""
    new_static_message_ar = f"""📦 Static Package

🔹 الأسعار:
- Static ISP Risk0: `{static_prices.get('ISP', '3')}$`
- Static Residential Verizon: `{static_prices.get('Verizon', '4')}$`  
- Static Residential AT&T: `{static_prices.get('ATT', '6')}$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{{}}`"""

    new_static_message_en = f"""📦 Static Package

🔹 Prices:
- Static ISP Risk0: {static_prices.get('ISP', '3')}$
- Static Residential Verizon: {static_prices.get('Verizon', '4')}$
- Static Residential AT&T: {static_prices.get('ATT', '6')}$

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
  cc849f22d5117db0b8fe5667e6d4b758

- Syriatel Cash:
  55973911
  14227865

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
  sohilskaf123@gmail.com

- Binance:
  1121540155

- Payeer:
  P1114452356

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: {{}}"""

    # تحديث الرسائل في الكود
    MESSAGES['ar']['static_package'] = new_static_message_ar
    MESSAGES['en']['static_package'] = new_static_message_en

def update_socks_messages(socks_prices):
    """تحديث رسائل بروكسي السوكس"""
    new_socks_message_ar = f"""📦 Socks Package
كافة دول العالم مع ميزة اختيار الولاية والمزود للبكج

🔹 الأسعار:
- باكج 5 بروكسيات مؤقتة: `{socks_prices.get('5proxy', '0.4')}$`
- باكج 10 بروكسيات مؤقتة: `{socks_prices.get('10proxy', '0.7')}$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{{}}`"""

    new_socks_message_en = f"""📦 Socks Package

🔹 Prices:
- 5 Temporary Proxies Package: {socks_prices.get('5proxy', '0.4')}$
- 10 Temporary Proxies Package: {socks_prices.get('10proxy', '0.7')}$

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
  cc849f22d5117db0b8fe5667e6d4b758

- Syriatel Cash:
  55973911
  14227865

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
  sohilskaf123@gmail.com

- Binance:
  1121540155

- Payeer:
  P1114452356

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: {{}}"""

    # تحديث الرسائل في الكود
    MESSAGES['ar']['socks_package'] = new_socks_message_ar
    MESSAGES['en']['socks_package'] = new_socks_message_en

def generate_order_id() -> str:
    """إنشاء معرف طلب فريد مكون من 16 خانة"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def get_user_language(user_id: int) -> str:
    """الحصول على لغة المستخدم"""
    user = db.get_user(user_id)
    return user[4] if user else 'ar'  # اللغة في العمود الخامس

def generate_transaction_number(transaction_type: str) -> str:
    """توليد رقم معاملة جديد"""
    # الحصول على آخر رقم معاملة من نفس النوع
    query = "SELECT MAX(id) FROM transactions WHERE transaction_type = ?"
    result = db.execute_query(query, (transaction_type,))
    
    last_id = 0
    if result and result[0][0]:
        last_id = result[0][0]
    
    # توليد الرقم الجديد
    new_id = last_id + 1
    
    if transaction_type == 'proxy':
        prefix = 'P'
    elif transaction_type == 'withdrawal':
        prefix = 'M'
    else:
        prefix = 'T'
    
    # تنسيق الرقم بـ 10 خانات
    transaction_number = f"{prefix}-{new_id:010d}"
    
    return transaction_number

def save_transaction(order_id: str, transaction_number: str, transaction_type: str, status: str = 'completed'):
    """حفظ بيانات المعاملة"""
    db.execute_query('''
        INSERT INTO transactions (order_id, transaction_number, transaction_type, status)
        VALUES (?, ?, ?, ?)
    ''', (order_id, transaction_number, transaction_type, status))

def update_order_status(order_id: str, status: str):
    """تحديث حالة الطلب"""
    if status == 'completed':
        db.execute_query('''
            UPDATE orders 
            SET status = 'completed', processed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (order_id,))
    elif status == 'failed':
        db.execute_query('''
            UPDATE orders 
            SET status = 'failed', processed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (order_id,))

async def handle_withdrawal_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة نجاح سحب الرصيد"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace('withdrawal_success_', '')
    
    # توليد رقم المعاملة
    transaction_number = generate_transaction_number('withdrawal')
    save_transaction(order_id, transaction_number, 'withdrawal', 'completed')
    
    # تحديث حالة الطلب إلى مكتمل
    update_order_status(order_id, 'completed')
    
    # الحصول على بيانات المستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        user = db.get_user(user_id)
        
        if user:
            user_language = get_user_language(user_id)
            withdrawal_amount = user[5]
            
            # تصفير رصيد المستخدم
            db.execute_query("UPDATE users SET referral_balance = 0 WHERE user_id = ?", (user_id,))
            
            # رسالة للمستخدم بلغته
            if user_language == 'ar':
                user_message = f"""✅ تم تسديد مكافأة الإحالة بنجاح!

💰 المبلغ: `{withdrawal_amount:.2f}$`
🆔 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`

🎉 تم إيداع المبلغ بنجاح!"""
            else:
                user_message = f"""✅ Referral reward paid successfully!

💰 Amount: `{withdrawal_amount:.2f}$`
🆔 Order ID: `{order_id}`
💳 Transaction Number: `{transaction_number}`

🎉 Amount deposited successfully!"""
            
            await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
            
            # إنشاء رسالة للأدمن مع زر فتح المحادثة
            keyboard = [
                [InlineKeyboardButton("💬 فتح محادثة مع المستخدم", url=f"tg://user?id={user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            admin_message = f"""✅ تم تسديد مكافأة الإحالة بنجاح!

👤 المستخدم: {user[2]} {user[3]}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 معرف المستخدم: `{user_id}`
💰 المبلغ المدفوع: `{withdrawal_amount:.2f}$`
🔗 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`

📋 تم نقل الطلب إلى الطلبات المكتملة."""
            
            await query.edit_message_text(admin_message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_withdrawal_failed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة فشل سحب الرصيد"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace('withdrawal_failed_', '')
    
    # توليد رقم المعاملة
    transaction_number = generate_transaction_number('withdrawal')
    save_transaction(order_id, transaction_number, 'withdrawal', 'failed')
    
    # تحديث حالة الطلب إلى فاشل
    update_order_status(order_id, 'failed')
    
    # الحصول على بيانات المستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        user = db.get_user(user_id)
        
        if user:
            user_language = get_user_language(user_id)
            withdrawal_amount = user[5]
            
            # رسالة للمستخدم
            if user_language == 'ar':
                user_message = f"""❌ فشلت عملية تسديد مكافأة الإحالة

💰 المبلغ: `{withdrawal_amount:.2f}$`
🆔 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`

📞 يرجى التواصل مع الإدارة لمعرفة السبب."""
            else:
                user_message = f"""❌ Referral reward payment failed

💰 Amount: `{withdrawal_amount:.2f}$`
🆔 Order ID: `{order_id}`
💳 Transaction Number: `{transaction_number}`

📞 Please contact admin to know the reason."""
            
            await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
            
            # رسالة للأدمن
            admin_message = f"""❌ فشلت عملية تسديد مكافأة الإحالة

👤 المستخدم: {user[2]} {user[3]}
🆔 معرف المستخدم: `{user_id}`
💰 المبلغ: `{withdrawal_amount:.2f}$`
🔗 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`

📋 تم نقل الطلب إلى الطلبات الفاشلة."""
            
            await query.edit_message_text(admin_message, parse_mode='Markdown')

async def change_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء عملية تغيير كلمة مرور الأدمن"""
    user_language = get_user_language(update.effective_user.id)
    
    if user_language == 'ar':
        message = "🔐 تغيير كلمة المرور\n\nيرجى إدخال كلمة المرور الحالية أولاً:"
    else:
        message = "🔐 Change Password\n\nPlease enter current password first:"
    
    await update.message.reply_text(message)
    context.user_data['password_change_step'] = 'current'
    return ADMIN_LOGIN

async def handle_password_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تغيير كلمة المرور"""
    step = context.user_data.get('password_change_step', 'current')
    user_language = get_user_language(update.effective_user.id)
    
    if step == 'current':
        # التحقق من كلمة المرور الحالية
        if update.message.text == ADMIN_PASSWORD:
            context.user_data['password_change_step'] = 'new'
            if user_language == 'ar':
                await update.message.reply_text("✅ كلمة المرور صحيحة\n\nيرجى إدخال كلمة المرور الجديدة:")
            else:
                await update.message.reply_text("✅ Password correct\n\nPlease enter new password:")
            return ADMIN_LOGIN
        else:
            if user_language == 'ar':
                await update.message.reply_text("❌ كلمة المرور غير صحيحة!")
            else:
                await update.message.reply_text("❌ Invalid password!")
            context.user_data.pop('password_change_step', None)
            return ConversationHandler.END
    
    elif step == 'new':
        # تحديث كلمة المرور
        global ADMIN_PASSWORD
        new_password = update.message.text
        ADMIN_PASSWORD = new_password
        
        # حفظ كلمة المرور الجديدة في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("admin_password", new_password)
        )
        
        if user_language == 'ar':
            await update.message.reply_text("✅ تم تغيير كلمة المرور بنجاح!")
        else:
            await update.message.reply_text("✅ Password changed successfully!")
        
        context.user_data.pop('password_change_step', None)
        return ConversationHandler.END
    
    return ConversationHandler.END

def validate_ip_address(ip: str) -> bool:
    """التحقق من صحة عنوان IP"""
    import re
    # نمط للتحقق من الهيكل: 1-3 أرقام.1-3 أرقام.1-3 أرقام.1-3 أرقام
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    return bool(re.match(pattern, ip))

def validate_port(port: str) -> bool:
    """التحقق من صحة رقم البورت"""
    # التحقق من أن المدخل رقمي وطوله 1-6 أرقام
    if not port.isdigit():
        return False
    
    port_int = int(port)
    # التحقق من أن الرقم بين 1 و 999999 (6 أرقام كحد أقصى)
    return 1 <= port_int <= 999999

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر البداية"""
    user = update.effective_user
    
    # التحقق من وجود المستخدم مسبقاً
    existing_user = db.get_user(user.id)
    is_new_user = existing_user is None
    
    # إضافة المستخدم إلى قاعدة البيانات
    referred_by = None
    if context.args and is_new_user:
        try:
            referred_by = int(context.args[0])
            # التأكد من أن المحيل موجود
            referrer = db.get_user(referred_by)
            if not referrer:
                referred_by = None
        except ValueError:
            pass
    
    db.add_user(user.id, user.username, user.first_name, user.last_name, referred_by)
    
    # إضافة مكافأة الإحالة للمحيل
    if referred_by and is_new_user:
        await add_referral_bonus(referred_by, user.id)
        
        # إشعار المحيل (بدون كشف الهوية)
        try:
            await context.bot.send_message(
                referred_by,
                f"🎉 تهانينا! انضم مستخدم جديد عبر رابط الإحالة الخاص بك.\n💰 تم إضافة `0.1$` إلى رصيدك!",
                parse_mode='Markdown'
            )
        except:
            pass  # في حالة عدم إمكانية إرسال الرسالة
        
        # إشعار الأدمن بانضمام عضو جديد عبر الإحالة
        await send_referral_notification(context, referred_by, user)
    
    db.log_action(user.id, "start_command")
    
    language = get_user_language(user.id)
    
    # رسالة ترحيب للمستخدمين الجدد
    if is_new_user:
        welcome_message = MESSAGES[language]['welcome']
        if referred_by:
            welcome_message += f"\n\n🎁 مرحباً بك! لقد انضممت عبر رابط إحالة وحصل صديقك على مكافأة!"
    else:
        welcome_message = f"مرحباً بعودتك {user.first_name}! 😊\n\n" + MESSAGES[language]['welcome']
    
    # إنشاء الأزرار الرئيسية
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][3]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تسجيل دخول الأدمن"""
    language = get_user_language(update.effective_user.id)
    await update.message.reply_text(MESSAGES[language]['admin_login_prompt'])
    return ADMIN_LOGIN

async def handle_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """التحقق من كلمة مرور الأدمن"""
    if update.message.text == ADMIN_PASSWORD:
        global ADMIN_CHAT_ID
        context.user_data['is_admin'] = True
        ADMIN_CHAT_ID = update.effective_user.id  # حفظ معرف الأدمن
        
        db.log_action(update.effective_user.id, "admin_login_success")
        
        # لوحة مفاتيح عادية للأدمن
        keyboard = [
            [KeyboardButton("📋 إدارة الطلبات")],
            [KeyboardButton("💰 إدارة الأموال"), KeyboardButton("👥 الإحالات")],
            [KeyboardButton("📢 البث"), KeyboardButton("🔍 استعلام عن مستخدم")],
            [KeyboardButton("⚙️ الإعدادات")],
            [KeyboardButton("🚪 تسجيل الخروج")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🔧 مرحباً بك في لوحة الأدمن\nاختر الخدمة المطلوبة:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END  # إنهاء المحادثة لتمكين إعادة الاستخدام
    else:
        await update.message.reply_text("كلمة المرور غير صحيحة!")
        return ConversationHandler.END

async def handle_static_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب البروكسي الستاتيك"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # حفظ نوع البروكسي فقط بدون إنشاء معرف الطلب
    context.user_data['proxy_type'] = 'static'
    
    db.log_action(user_id, "static_proxy_request_started")
    
    # عرض رسالة الحزمة بدون معرف الطلب
    package_message = MESSAGES[language]['static_package'].replace('معرف الطلب: `{}`', 'سيتم إنشاء معرف الطلب بعد إرسال إثبات الدفع')
    await update.message.reply_text(package_message, parse_mode='Markdown')
    
    # عرض قائمة الدول للستاتيك
    keyboard = []
    for code, name in STATIC_COUNTRIES[language].items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"country_{code}")])
    keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_country")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        MESSAGES[language]['select_country'],
        reply_markup=reply_markup
    )

async def handle_socks_proxy_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب بروكسي السوكس"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # حفظ نوع البروكسي فقط بدون إنشاء معرف الطلب
    context.user_data['proxy_type'] = 'socks'
    
    db.log_action(user_id, "socks_proxy_request_started")
    
    # عرض رسالة الحزمة بدون معرف الطلب
    package_message = MESSAGES[language]['socks_package'].replace('معرف الطلب: `{}`', 'سيتم إنشاء معرف الطلب بعد إرسال إثبات الدفع')
    await update.message.reply_text(package_message, parse_mode='Markdown')
    
    # عرض قائمة الدول للسوكس (مع دول إضافية)
    keyboard = []
    for code, name in SOCKS_COUNTRIES[language].items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"country_{code}")])
    keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_country")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        MESSAGES[language]['select_country'],
        reply_markup=reply_markup
    )

async def handle_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة اختيار الدولة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    if query.data == "manual_country":
        # الإدخال اليدوي للدولة
        await query.edit_message_text("يرجى إدخال اسم الدولة يدوياً:")
        context.user_data['waiting_for'] = 'manual_country'
        return
    
    elif query.data == "manual_state":
        # الإدخال اليدوي للولاية
        await query.edit_message_text("يرجى إدخال اسم الولاية/المنطقة يدوياً:")
        context.user_data['waiting_for'] = 'manual_state'
        return
    
    elif query.data.startswith("country_"):
        country_code = query.data.replace("country_", "")
        # حفظ اسم الدولة الكامل مع العلم بدلاً من الرمز فقط
        proxy_type = context.user_data.get('proxy_type', 'static')
        if proxy_type == 'socks':
            country_name = SOCKS_COUNTRIES[language].get(country_code, country_code)
        else:
            country_name = STATIC_COUNTRIES[language].get(country_code, country_code)
        context.user_data['selected_country'] = country_name
        context.user_data['selected_country_code'] = country_code
        
        # عرض قائمة الولايات بناء على الدولة
        states_data = get_states_for_country(country_code)
        if states_data:
            states = states_data[language]
        else:
            # للدول الأخرى، انتقل مباشرة لطرق الدفع
            await show_payment_methods(query, context, language)
            return
        
        keyboard = []
        for code, name in states.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"state_{code}")])
        keyboard.append([InlineKeyboardButton(MESSAGES[language]['manual_input'], callback_data="manual_state")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            MESSAGES[language]['select_state'],
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("state_"):
        state_code = query.data.replace("state_", "")
        # حفظ اسم الولاية الكامل بدلاً من الرمز فقط
        country_code = context.user_data.get('selected_country_code', '')
        states_data = get_states_for_country(country_code)
        if states_data:
            state_name = states_data[language].get(state_code, state_code)
        else:
            state_name = state_code
        context.user_data['selected_state'] = state_name
        await show_payment_methods(query, context, language)

async def show_payment_methods(query, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
    """عرض طرق الدفع"""
    keyboard = [
        [InlineKeyboardButton("💳 شام كاش", callback_data="payment_shamcash")],
        [InlineKeyboardButton("💳 سيرياتيل كاش", callback_data="payment_syriatel")],
        [InlineKeyboardButton("🪙 Coinex", callback_data="payment_coinex")],
        [InlineKeyboardButton("🪙 Binance", callback_data="payment_binance")],
        [InlineKeyboardButton("🪙 Payeer", callback_data="payment_payeer")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        MESSAGES[language]['payment_methods'],
        reply_markup=reply_markup
    )

async def handle_payment_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار طريقة الدفع"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    payment_method = query.data.replace("payment_", "")
    context.user_data['payment_method'] = payment_method
    
    await query.edit_message_text(MESSAGES[language]['send_payment_proof'])
    
    return PAYMENT_PROOF

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إثبات الدفع"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # التحقق من وجود البيانات المطلوبة
    if 'proxy_type' not in context.user_data:
        await update.message.reply_text(
            "❌ خطأ: لم يتم العثور على نوع البروكسي. يرجى البدء من جديد بالضغط على /start",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # إنشاء معرف الطلب الآن فقط عند إرسال إثبات الدفع
    order_id = generate_order_id()
    context.user_data['current_order_id'] = order_id
    
    # إنشاء الطلب في قاعدة البيانات
    proxy_type = context.user_data.get('proxy_type', 'static')
    country = context.user_data.get('selected_country', 'manual')
    state = context.user_data.get('selected_state', 'manual')
    payment_method = context.user_data.get('payment_method', 'unknown')
    
    db.create_order(order_id, user_id, proxy_type, country, state, payment_method)
    
    # حفظ إثبات الدفع
    if update.message.photo:
        # إذا كانت صورة
        file_id = update.message.photo[-1].file_id
        payment_proof = f"photo:{file_id}"
        
        # إرسال نسخة للمستخدم
        await update.message.reply_photo(
            photo=file_id,
            caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`\n\n✅ تم حفظ إثبات الدفع",
            parse_mode='Markdown'
        )
    else:
        # إذا كان نص
        payment_proof = f"text:{update.message.text}"
        
        # إرسال نسخة للمستخدم
        await update.message.reply_text(
            f"📝 إثبات دفع للطلب بمعرف: `{order_id}`\n\nالتفاصيل:\n{update.message.text}\n\n✅ تم حفظ إثبات الدفع",
            parse_mode='Markdown'
        )
    
    db.update_order_payment_proof(order_id, payment_proof)
    
    # إرسال نسخة من الطلب للمستخدم
    await send_order_copy_to_user(update, context, order_id)
    
    # إرسال إشعار للأدمن مع زر المعالجة
    await send_admin_notification(context, order_id, payment_proof)
    
    await update.message.reply_text(MESSAGES[language]['order_received'], parse_mode='Markdown')
    
    db.log_action(user_id, "payment_proof_submitted", order_id)
    
    return ConversationHandler.END

async def send_withdrawal_notification(context: ContextTypes.DEFAULT_TYPE, withdrawal_id: str, user: tuple) -> None:
    """إرسال إشعار طلب سحب للأدمن"""
    message = f"""💸 طلب سحب رصيد جديد

👤 الاسم: {user[2]} {user[3]}
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 معرف المستخدم: `{user[0]}`

━━━━━━━━━━━━━━━
💰 المبلغ المطلوب: `{user[5]:.2f}$`
📊 نوع الطلب: سحب رصيد الإحالات

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{withdrawal_id}`
📅 تاريخ الطلب: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    # زر معالجة طلب السحب
    keyboard = [[InlineKeyboardButton("💸 معالجة طلب السحب", callback_data=f"process_{withdrawal_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                ADMIN_CHAT_ID, 
                message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"خطأ في إرسال إشعار طلب السحب: {e}")
    
    # حفظ الإشعار في قاعدة البيانات
    db.log_action(user[0], "withdrawal_notification", f"New withdrawal: {withdrawal_id}")

async def send_referral_notification(context: ContextTypes.DEFAULT_TYPE, referrer_id: int, new_user) -> None:
    """إرسال إشعار للأدمن بانضمام عضو جديد عبر الإحالة"""
    # الحصول على بيانات المحيل
    referrer = db.get_user(referrer_id)
    
    if referrer:
        message = f"""👥 عضو جديد عبر الإحالة

🆕 العضو الجديد:
👤 الاسم: {new_user.first_name} {new_user.last_name or ''}
📱 اسم المستخدم: @{new_user.username or 'غير محدد'}
🆔 معرف المستخدم: `{new_user.id}`

━━━━━━━━━━━━━━━
👥 تم إحالته بواسطة:
👤 الاسم: {referrer[2]} {referrer[3]}
📱 اسم المستخدم: @{referrer[1] or 'غير محدد'}
🆔 معرف المحيل: `{referrer[0]}`

━━━━━━━━━━━━━━━
💰 تم إضافة `0.1$` لرصيد المحيل
📅 تاريخ الانضمام: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        if ADMIN_CHAT_ID:
            try:
                await context.bot.send_message(
                    ADMIN_CHAT_ID, 
                    message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"خطأ في إرسال إشعار الإحالة: {e}")
        
        # حفظ الإشعار في قاعدة البيانات
        db.log_action(new_user.id, "referral_notification", f"Referred by: {referrer_id}")

async def send_order_copy_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str) -> None:
    """إرسال نسخة من الطلب للمستخدم"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # الحصول على تفاصيل الطلب
    query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(query, (order_id,))
    
    if result:
        order = result[0]
        
        # تحديد طريقة الدفع باللغة المناسبة
        payment_methods = {
            'ar': {
                'shamcash': 'شام كاش',
                'syriatel': 'سيرياتيل كاش', 
                'coinex': 'Coinex',
                'binance': 'Binance',
                'payeer': 'Payeer'
            },
            'en': {
                'shamcash': 'Sham Cash',
                'syriatel': 'Syriatel Cash',
                'coinex': 'Coinex', 
                'binance': 'Binance',
                'payeer': 'Payeer'
            }
        }
        
        payment_method = payment_methods[language].get(order[5], order[5])
        
        if language == 'ar':
            message = f"""📋 نسخة من طلبك
            
👤 الاسم: `{order[12]} {order[13] or ''}`
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
🔧 نوع البروكسي: {order[2]}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{order[0]}`
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ تحت المراجعة

يرجى الاحتفاظ بمعرف الطلب للمراجعة المستقبلية."""
        else:
            message = f"""📋 Copy of Your Order
            
👤 Name: `{order[12]} {order[13] or ''}`
🆔 User ID: `{order[1]}`

━━━━━━━━━━━━━━━
📦 Order Details:
🔧 Proxy Type: {order[2]}
🌍 Country: {order[3]}
🏠 State: {order[4]}

━━━━━━━━━━━━━━━
💳 Payment Details:
💰 Payment Method: {payment_method}

━━━━━━━━━━━━━━━
🔗 Order ID: `{order[0]}`
📅 Order Date: {order[9]}
📊 Status: ⏳ Under Review

Please keep the order ID for future reference."""
        
        await context.bot.send_message(user_id, message, parse_mode='Markdown')

async def send_admin_notification(context: ContextTypes.DEFAULT_TYPE, order_id: str, payment_proof: str = None) -> None:
    """إرسال إشعار للأدمن بطلب جديد"""
    # الحصول على تفاصيل الطلب
    query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(query, (order_id,))
    
    if result:
        order = result[0]
        
        # تحديد طريقة الدفع باللغة العربية
        payment_methods_ar = {
            'shamcash': 'شام كاش',
            'syriatel': 'سيرياتيل كاش',
            'coinex': 'Coinex',
            'binance': 'Binance',
            'payeer': 'Payeer'
        }
        
        payment_method_ar = payment_methods_ar.get(order[5], order[5])
        
        message = f"""🔔 طلب جديد

👤 الاسم: `{order[12]} {order[13] or ''}`
📱 اسم المستخدم: @{order[14] or 'غير محدد'}
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
🔧 نوع البروكسي: {order[2]}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{order[0]}`
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ معلق"""
        
        keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # حفظ رسالة إثبات الدفع مع معرف الطلب
        if order[7]:  # payment_proof
            proof_message = f"إثبات دفع للطلب بمعرف: {order_id}"
            db.execute_query(
                "INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)",
                (order[1], "payment_proof_saved", proof_message)
            )
        
        # إرسال للأدمن مع زر المعالجة
        keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if ADMIN_CHAT_ID:
            try:
                # إرسال الإشعار الرئيسي
                main_msg = await context.bot.send_message(
                    ADMIN_CHAT_ID, 
                    message, 
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
                # إرسال إثبات الدفع كرد على رسالة الطلب
                if payment_proof:
                    if payment_proof.startswith("photo:"):
                        file_id = payment_proof.replace("photo:", "")
                        await context.bot.send_photo(
                            ADMIN_CHAT_ID,
                            photo=file_id,
                            caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`",
                            parse_mode='Markdown',
                            reply_to_message_id=main_msg.message_id
                        )
                    elif payment_proof.startswith("text:"):
                        text_proof = payment_proof.replace("text:", "")
                        await context.bot.send_message(
                            ADMIN_CHAT_ID,
                            f"📝 إثبات دفع للطلب بمعرف: `{order_id}`\n\nالنص:\n{text_proof}",
                            parse_mode='Markdown',
                            reply_to_message_id=main_msg.message_id
                        )
                
            except Exception as e:
                print(f"خطأ في إرسال إشعار الأدمن: {e}")
        
        # حفظ تفاصيل الطلب في قاعدة البيانات
        db.log_action(order[1], "order_details_logged", f"Order: {order_id} - {order[2]} - {order[3]}")

async def handle_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قسم الإحالات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء رابط الإحالة
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
    except:
        bot_username = "your_bot"  # fallback if bot info fails
    
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    # الحصول على رصيد الإحالة
    user = db.get_user(user_id)
    referral_balance = user[5] if user else 0.0
    
    # عدد الإحالات
    query = "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?"
    referral_count = db.execute_query(query, (user_id,))[0][0]
    
    if language == 'ar':
        message = f"""👥 نظام الإحالات

🔗 رابط الإحالة الخاص بك:
`{referral_link}`

💰 رصيدك: `{referral_balance:.2f}$`
👥 عدد إحالاتك: `{referral_count}`

━━━━━━━━━━━━━━━
شارك رابطك واحصل على `0.1$` لكل إحالة!
الحد الأدنى للسحب: `1.0$`"""
    else:
        message = f"""👥 Referral System

🔗 Your referral link:
`{referral_link}`

💰 Your balance: `{referral_balance:.2f}$`
👥 Your referrals: `{referral_count}`

━━━━━━━━━━━━━━━
Share your link and earn `0.1$` per referral!
Minimum withdrawal: `1.0$`"""
    
    keyboard = [
        [InlineKeyboardButton("💸 سحب الرصيد" if language == 'ar' else "💸 Withdraw Balance", callback_data="withdraw_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الإعدادات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🌐 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🌐 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "اختر اللغة / Choose Language:",
        reply_markup=reply_markup
    )

async def handle_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تغيير اللغة"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "lang_ar":
        new_language = "ar"
        message = """تم تغيير اللغة إلى العربية ✅
يرجى استخدام الأمر /start لإعادة تحميل القوائم

Language changed to Arabic ✅  
Please use /start command to reload menus"""
    else:
        new_language = "en"
        message = """Language changed to English ✅
Please use /start command to reload menus

تم تغيير اللغة إلى الإنجليزية ✅
يرجى استخدام الأمر /start لإعادة تحميل القوائم"""
    
    db.update_user_language(user_id, new_language)
    db.log_action(user_id, "language_change", new_language)
    
    await query.edit_message_text(message)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الاستعلامات المرسلة"""
    query = update.callback_query
    
    if query.data.startswith("country_") or query.data.startswith("state_") or query.data in ["manual_country", "manual_state"]:
        await handle_country_selection(update, context)
    elif query.data.startswith("payment_"):
        await handle_payment_method_selection(update, context)
    elif query.data.startswith("lang_"):
        await handle_language_change(update, context)
    # تم نقل معالجة process_ إلى process_order_conv_handler
    # تم نقل معالجة payment_success و payment_failed إلى process_order_conv_handler
    # تم نقل معالجة proxy_type_ إلى process_order_conv_handler
    # تم نقل معالجة admin_country_ و admin_state_ إلى process_order_conv_handler
    elif query.data in ["manage_orders", "show_pending_orders", "admin_referrals", "user_lookup", "manage_money", "admin_settings", "reset_balance"]:
        await handle_admin_menu_actions(update, context)
    elif query.data == "withdraw_balance":
        await handle_withdrawal_request(update, context)
    elif query.data in ["confirm_logout", "cancel_logout"]:
        await handle_logout_confirmation(update, context)
    elif query.data == "back_to_admin":
        await handle_back_to_admin(update, context)
    elif query.data in ["send_custom_message", "no_custom_message"]:
        await handle_custom_message_choice(update, context)
    elif query.data == "send_proxy_confirm":
        thank_message = context.user_data.get('admin_thank_message', '')
        await send_proxy_to_user(update, context, thank_message)
        await query.edit_message_text("✅ تم إرسال البروكسي للمستخدم بنجاح!")
    elif query.data == "cancel_proxy_send":
        await query.edit_message_text("❌ تم إلغاء إرسال البروكسي. يمكنك البدء من جديد إذا أردت.")
    elif query.data.startswith("quiet_"):
        await handle_quiet_hours_selection(update, context)
    elif query.data in ["confirm_clear_db", "cancel_clear_db"]:
        await handle_database_clear(update, context)
    elif query.data == "cancel_processing":
        await handle_cancel_processing(update, context)
    elif query.data.startswith("withdrawal_success_"):
        await handle_withdrawal_success(update, context)
    elif query.data.startswith("withdrawal_failed_"):
        await handle_withdrawal_failed(update, context)

    else:
        await query.answer("قيد التطوير...")

async def handle_admin_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار الدولة من قبل الأدمن"""
    query = update.callback_query
    await query.answer()
    
    # معالجة التنقل بين الصفحات
    if query.data.startswith("admin_country_page_"):
        page = int(query.data.replace("admin_country_page_", ""))
        proxy_type = context.user_data.get('admin_proxy_type', 'static')
        countries = SOCKS_COUNTRIES['ar'] if proxy_type == 'socks' else STATIC_COUNTRIES['ar']
        
        reply_markup = create_paginated_keyboard(countries, "admin_country_", page, 8, 'ar')
        await query.edit_message_text("4️⃣ اختر الدولة:", reply_markup=reply_markup)
        return ENTER_COUNTRY
    
    # معالجة التنقل بين صفحات الولايات
    elif query.data.startswith("admin_state_page_"):
        page = int(query.data.replace("admin_state_page_", ""))
        country_code = context.user_data.get('current_country_code', '')
        states = get_states_for_country(country_code)
        
        if states:
            reply_markup = create_paginated_keyboard(states['ar'], "admin_state_", page, 8, 'ar')
            await query.edit_message_text("5️⃣ اختر الولاية:", reply_markup=reply_markup)
        return ENTER_STATE
    
    elif query.data == "admin_country_other":
        context.user_data['admin_input_state'] = ENTER_COUNTRY
        await query.edit_message_text("4️⃣ يرجى إدخال اسم الدولة:")
        return ENTER_COUNTRY
    
    elif query.data.startswith("admin_state_"):
        if query.data == "admin_state_other":
            context.user_data['admin_input_state'] = ENTER_STATE
            await query.edit_message_text("5️⃣ يرجى إدخال اسم الولاية:")
            return ENTER_STATE
        else:
            state_code = query.data.replace("admin_state_", "")
            country_code = context.user_data.get('current_country_code', '')
            states = get_states_for_country(country_code)
            
            if states:
                context.user_data['admin_proxy_state'] = states['ar'].get(state_code, state_code)
            else:
                context.user_data['admin_proxy_state'] = state_code
                
            context.user_data['admin_input_state'] = ENTER_USERNAME
            await query.edit_message_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:")
            return ENTER_USERNAME
    
    else:
        country_code = query.data.replace("admin_country_", "")
        context.user_data['current_country_code'] = country_code
        
        # تحديد قائمة الدول المناسبة
        proxy_type = context.user_data.get('admin_proxy_type', 'static')
        if proxy_type == 'socks':
            context.user_data['admin_proxy_country'] = SOCKS_COUNTRIES['ar'].get(country_code, country_code)
        else:
            context.user_data['admin_proxy_country'] = STATIC_COUNTRIES['ar'].get(country_code, country_code)
        
        # عرض قائمة الولايات إذا كانت متوفرة
        states = get_states_for_country(country_code)
        
        if states:
            reply_markup = create_paginated_keyboard(states['ar'], "admin_state_", 0, 8, 'ar')
            await query.edit_message_text("5️⃣ اختر الولاية:", reply_markup=reply_markup)
            return ENTER_STATE
        else:
            # انتقل مباشرة لاسم المستخدم
            context.user_data['admin_input_state'] = ENTER_USERNAME
            await query.edit_message_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:")
            return ENTER_USERNAME

async def handle_withdrawal_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة طلب سحب الرصيد"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    language = get_user_language(user_id)
    
    if user and user[5] >= 1.0:  # الحد الأدنى 1 دولار
        # إنشاء معرف طلب السحب
        withdrawal_id = generate_order_id()
        
        # حفظ طلب السحب في قاعدة البيانات
        db.execute_query(
            "INSERT INTO orders (id, user_id, proxy_type, payment_amount, status) VALUES (?, ?, ?, ?, ?)",
            (withdrawal_id, user_id, 'withdrawal', user[5], 'pending')
        )
        
        if language == 'ar':
            message = f"""💸 تم إرسال طلب سحب الرصيد

💰 المبلغ المطلوب: `{user[5]:.2f}$`
🆔 معرف الطلب: `{withdrawal_id}`

تم إرسال طلبك للأدمن وسيتم معالجته في أقرب وقت ممكن."""
        else:
            message = f"""💸 Withdrawal request sent

💰 Amount: `{user[5]:.2f}$`
🆔 Request ID: `{withdrawal_id}`

Your request has been sent to admin and will be processed soon."""
        
        # إرسال إشعار طلب السحب للأدمن
        await send_withdrawal_notification(context, withdrawal_id, user)
        
        await query.edit_message_text(message, parse_mode='Markdown')
    else:
        min_amount = 1.0
        current_balance = user[5] if user else 0.0
        
        if language == 'ar':
            message = f"""❌ رصيد غير كافٍ للسحب

💰 رصيدك الحالي: `{current_balance:.2f}$`
📊 الحد الأدنى للسحب: `{min_amount:.1f}$`

يرجى دعوة المزيد من الأصدقاء لزيادة رصيدك!"""
        else:
            message = f"""❌ Insufficient balance for withdrawal

💰 Current balance: `{current_balance:.2f}$`
📊 Minimum withdrawal: `{min_amount:.1f}$`

Please invite more friends to increase your balance!"""
        
        await query.edit_message_text(message, parse_mode='Markdown')

async def handle_custom_message_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار إرسال رسالة مخصصة"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    if query.data == "send_custom_message":
        await query.edit_message_text("يرجى إدخال الرسالة المخصصة للمستخدم:")
        return CUSTOM_MESSAGE
    else:
        # عدم إرسال رسالة مخصصة
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            user_language = get_user_language(user_id)
            
            # إرسال رسالة فشل العملية مع معلومات الدعم
            failure_message = {
                'ar': f"""❌ تم رفض طلبك رقم `{order_id}`

إن كان لديك استفسار، يرجى التواصل مع الدعم:
@Static_support""",
                'en': f"""❌ Your order `{order_id}` has been rejected

If you have any questions, please contact support:
@Static_support"""
            }
            
            await context.bot.send_message(
                user_id,
                failure_message[user_language],
                parse_mode='Markdown'
            )
        
        # جدولة حذف الطلب بعد 48 ساعة
        await schedule_order_deletion(context, order_id, user_id if user_result else None)
        
        await query.edit_message_text(f"تم إشعار المستخدم برفض الطلب.\nمعرف الطلب: `{order_id}`\n\n⏰ سيتم حذف الطلب تلقائياً بعد 48 ساعة", parse_mode='Markdown')
        return ConversationHandler.END

async def handle_custom_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال الرسالة المخصصة"""
    custom_message = update.message.text
    order_id = context.user_data['processing_order_id']
    
    # إرسال الرسالة المخصصة للمستخدم
    user_query = "SELECT user_id FROM orders WHERE id = ?"
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id = user_result[0][0]
        user_language = get_user_language(user_id)
        
        # إرسال الرسالة المخصصة في قالب جاهز
        admin_message_template = f"""📩 لديك رسالة من الأدمن

"{custom_message}"

━━━━━━━━━━━━━━━━━"""
        
        await context.bot.send_message(user_id, admin_message_template)
        
        # إرسال رسالة فشل العملية
        failure_message = {
            'ar': f"""❌ تم رفض طلبك رقم `{order_id}`

إن كان لديك استفسار، يرجى التواصل مع الدعم:
@Static_support""",
            'en': f"""❌ Your order `{order_id}` has been rejected

If you have any questions, please contact support:
@Static_support"""
        }
        
        await context.bot.send_message(
            user_id,
            failure_message[user_language],
            parse_mode='Markdown'
        )
        
        # جدولة حذف الطلب بعد 48 ساعة
        await schedule_order_deletion(context, order_id, user_id)
    
    await update.message.reply_text(f"تم إرسال الرسالة المخصصة ورسالة فشل العملية للمستخدم.\nمعرف الطلب: {order_id}\n\n⏰ سيتم حذف الطلب تلقائياً بعد 48 ساعة")
    return ConversationHandler.END

async def schedule_order_deletion(context: ContextTypes.DEFAULT_TYPE, order_id: str, user_id: int = None) -> None:
    """جدولة حذف الطلب بعد 48 ساعة"""
    import asyncio
    
    async def delete_after_48_hours():
        # انتظار 48 ساعة (48 * 60 * 60 ثانية)
        await asyncio.sleep(48 * 60 * 60)
        
        try:
            # حذف الطلب من قاعدة البيانات
            db.execute_query("DELETE FROM orders WHERE id = ? AND status = 'failed'", (order_id,))
            
            # إشعار المستخدم بانتهاء صلاحية الطلب
            if user_id:
                user_language = get_user_language(user_id)
                failure_message = {
                    'ar': f"⏰ انتهت صلاحية الطلب `{order_id}` وتم حذفه من النظام.\n\n💡 يمكنك إنشاء طلب جديد في أي وقت.",
                    'en': f"⏰ Order `{order_id}` has expired and been deleted from the system.\n\n💡 You can create a new order anytime."
                }
                
                await context.bot.send_message(
                    user_id,
                    failure_message[user_language],
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Error deleting expired order {order_id}: {e}")
    
    # تشغيل المهمة في الخلفية
    context.application.create_task(delete_after_48_hours())

# إضافة المزيد من الوظائف المساعدة
async def add_referral_bonus(user_id: int, referred_user_id: int) -> None:
    """إضافة مكافأة الإحالة"""
    # الحصول على قيمة الإحالة من الإعدادات
    referral_amount_query = "SELECT value FROM settings WHERE key = 'referral_amount'"
    result = db.execute_query(referral_amount_query)
    referral_amount = float(result[0][0]) if result else 0.1
    
    # إضافة الإحالة
    db.execute_query(
        "INSERT INTO referrals (referrer_id, referred_id, amount) VALUES (?, ?, ?)",
        (user_id, referred_user_id, referral_amount)
    )
    
    # تحديث رصيد المستخدم
    db.execute_query(
        "UPDATE users SET referral_balance = referral_balance + ? WHERE user_id = ?",
        (referral_amount, user_id)
    )

async def cleanup_old_orders() -> None:
    """تنظيف الطلبات القديمة (48 ساعة)"""
    # حذف الطلبات الفاشلة القديمة (بعد 48 ساعة كما هو مطلوب في المواصفات)
    deleted_failed = db.execute_query("""
        DELETE FROM orders 
        WHERE status = 'failed' 
        AND created_at < datetime('now', '-48 hours')
    """)
    
    # تسجيل عدد الطلبات المحذوفة
    if deleted_failed:
        print(f"تم حذف {len(deleted_failed)} طلب فاشل قديم")
    
    # يمكن الاحتفاظ بالطلبات المكتملة للإحصائيات (لا نحذفها)

# تشغيل تنظيف الطلبات كل ساعة
async def schedule_cleanup():
    """جدولة تنظيف الطلبات"""
    while True:
        await asyncio.sleep(3600)  # كل ساعة
        await cleanup_old_orders()

def create_requirements_file():
    """إنشاء ملف requirements.txt"""
    requirements = """python-telegram-bot==20.7
pandas>=1.3.0
openpyxl>=3.0.0"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)

async def export_database_excel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير قاعدة البيانات إلى Excel"""
    try:
        # قراءة البيانات من قاعدة البيانات
        conn = sqlite3.connect(DATABASE_FILE)
        
        # إنشاء ملف Excel مع عدة أوراق
        with pd.ExcelWriter('database_export.xlsx', engine='openpyxl') as writer:
            # جدول المستخدمين
            users_df = pd.read_sql_query("SELECT * FROM users", conn)
            users_df.to_excel(writer, sheet_name='Users', index=False)
            
            # جدول الطلبات
            orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
            orders_df.to_excel(writer, sheet_name='Orders', index=False)
            
            # جدول الإحالات
            referrals_df = pd.read_sql_query("SELECT * FROM referrals", conn)
            referrals_df.to_excel(writer, sheet_name='Referrals', index=False)
            
            # جدول السجلات
            logs_df = pd.read_sql_query("SELECT * FROM logs", conn)
            logs_df.to_excel(writer, sheet_name='Logs', index=False)
        
        conn.close()
        
        # إرسال الملف
        with open('database_export.xlsx', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                caption="📊 تم تصدير قاعدة البيانات بصيغة Excel"
            )
        
        # حذف الملف المؤقت
        os.remove('database_export.xlsx')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير Excel: {str(e)}")

async def export_database_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير قاعدة البيانات إلى CSV"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        
        # تصدير جدول المستخدمين
        users_df = pd.read_sql_query("SELECT * FROM users", conn)
        users_df.to_csv('users_export.csv', index=False, encoding='utf-8-sig')
        
        # تصدير جدول الطلبات
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        orders_df.to_csv('orders_export.csv', index=False, encoding='utf-8-sig')
        
        conn.close()
        
        # إرسال الملفات
        with open('users_export.csv', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption="👥 بيانات المستخدمين - CSV"
            )
        
        with open('orders_export.csv', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption="📋 بيانات الطلبات - CSV"
            )
        
        # حذف الملفات المؤقتة
        os.remove('users_export.csv')
        os.remove('orders_export.csv')
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير CSV: {str(e)}")

async def export_database_sqlite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تصدير ملف قاعدة البيانات الأصلي"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"proxy_bot_backup_{timestamp}.db"
        
        # نسخ ملف قاعدة البيانات
        import shutil
        shutil.copy2(DATABASE_FILE, backup_filename)
        
        # إرسال الملف
        with open(backup_filename, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=backup_filename,
                caption="🗃️ نسخة احتياطية من قاعدة البيانات - SQLite"
            )
        
        # حذف الملف المؤقت
        os.remove(backup_filename)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تصدير قاعدة البيانات: {str(e)}")

def create_readme_file():
    """إنشاء ملف README.md"""
    readme_content = """# بوت بيع البروكسيات - Proxy Sales Bot

## تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

## إعداد البوت

1. احصل على TOKEN من BotFather على تيليجرام
2. ضع التوكن في متغير TOKEN في الكود
3. قم بتشغيل البوت:

```bash
python simpl_bot.py
```

## الميزات

- طلب البروكسيات (Static/Socks)
- نظام دفع متعدد الطرق
- إدارة أدمن متكاملة
- نظام إحالات
- دعم اللغتين العربية والإنجليزية
- قاعدة بيانات SQLite محلية

## أوامر الأدمن

- `/admin_login` - تسجيل دخول الأدمن
- كلمة المرور: `sohilSOHIL`

## البنية

- `simpl_bot.py` - الملف الرئيسي للبوت
- `proxy_bot.db` - قاعدة البيانات (تُنشأ تلقائياً)
- `requirements.txt` - متطلبات Python
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

async def handle_process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة الطلب من قبل الأدمن"""
    query = update.callback_query
    await query.answer()
    
    order_id = query.data.replace("process_", "")
    context.user_data['processing_order_id'] = order_id
    
    keyboard = [
        [InlineKeyboardButton("نعم", callback_data="payment_success")],
        [InlineKeyboardButton("لا", callback_data="payment_failed")],
        [InlineKeyboardButton("⏸️ إلغاء المعالجة مؤقتاً", callback_data="cancel_processing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "هل عملية الدفع ناجحة وحقيقية؟",
        reply_markup=reply_markup
    )
    
    return PROCESS_ORDER

async def handle_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة نجاح الدفع والبدء في جمع معلومات البروكسي"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    # توليد رقم المعاملة وحفظها
    transaction_number = generate_transaction_number('proxy')
    save_transaction(order_id, transaction_number, 'proxy', 'completed')
    
    # تحديث حالة الطلب إلى مكتمل
    update_order_status(order_id, 'completed')
    
    # إرسال رسالة للمستخدم أن الطلب قيد المعالجة
    order_query = "SELECT user_id, proxy_type FROM orders WHERE id = ?"
    order_result = db.execute_query(order_query, (order_id,))
    if order_result:
        user_id = order_result[0][0]
        order_type = order_result[0][1]
        user_language = get_user_language(user_id)
        
        # رسالة للمستخدم مع رقم المعاملة
        if user_language == 'ar':
            user_message = f"""✅ تم قبول دفعتك بنجاح!

🆔 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`
📦 نوع الباكج: {order_type}

🔄 سيتم معالجة طلبك وإرسال البيانات قريباً."""
        else:
            user_message = f"""✅ Your payment has been accepted successfully!

🆔 Order ID: `{order_id}`
💳 Transaction Number: `{transaction_number}`
📦 Package Type: {order_type}

🔄 Your order will be processed and data sent soon."""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
        
        # التحقق من نوع الطلب
        if order_type == 'withdrawal':
            # معالجة طلب السحب
            await handle_withdrawal_approval(query, context, order_id, user_id)
            return ConversationHandler.END
    
    # رسالة للأدمن مع رقم المعاملة ونوع البروكسي
    proxy_type_ar = "بروكسي ستاتيك" if order_type == "static" else "بروكسي سوكس" if order_type == "socks" else order_type
    
    admin_message = f"""✅ تم قبول الدفع للطلب

🆔 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`
👤 معرف المستخدم: `{user_id}`
📝 الطلب: {proxy_type_ar}

📋 الطلب جاهز للمعالجة والإرسال للمستخدم."""
    
    # إنشاء رسالة جديدة بدلاً من تعديل الرسالة الأصلية
    keyboard = [
        [InlineKeyboardButton("ستاتيك", callback_data="proxy_type_static")],
        [InlineKeyboardButton("سوكس", callback_data="proxy_type_socks")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # إرسال رسالة جديدة بدلاً من تعديل الرسالة الموجودة
    await context.bot.send_message(
        update.effective_chat.id,
        "1️⃣ اختر نوع البروكسي:",
        reply_markup=reply_markup
    )
    
    # تحديث الرسالة الأصلية لتوضيح أنه تم البدء في المعالجة
    await query.edit_message_text(
        admin_message,
        parse_mode='Markdown'
    )
    
    return ENTER_PROXY_TYPE

async def handle_withdrawal_approval(query, context: ContextTypes.DEFAULT_TYPE, order_id: str, user_id: int) -> None:
    """معالجة طلب السحب مع خيارات النجاح/الفشل"""
    
    # إنشاء أزرار النجاح والفشل
    keyboard = [
        [InlineKeyboardButton("✅ تم التسديد", callback_data=f"withdrawal_success_{order_id}")],
        [InlineKeyboardButton("❌ فشلت المعاملة", callback_data=f"withdrawal_failed_{order_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💰 معالجة طلب سحب الرصيد\n\n🆔 معرف الطلب: `{order_id}`\n\nاختر حالة المعاملة:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_payment_failed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة فشل الدفع"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data['processing_order_id']
    
    # توليد رقم المعاملة وحفظها
    transaction_number = generate_transaction_number('proxy')
    save_transaction(order_id, transaction_number, 'proxy', 'failed')
    
    # تحديث حالة الطلب إلى فاشل
    update_order_status(order_id, 'failed')
    
    # إرسال رسالة للمستخدم
    order_query = "SELECT user_id, proxy_type FROM orders WHERE id = ?"
    order_result = db.execute_query(order_query, (order_id,))
    if order_result:
        user_id = order_result[0][0]
        order_type = order_result[0][1]
        user_language = get_user_language(user_id)
        
        # رسالة للمستخدم مع رقم المعاملة
        if user_language == 'ar':
            user_message = f"""❌ تم رفض دفعتك

🆔 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`
📦 نوع الباكج: {order_type}

📞 يرجى التواصل مع الإدارة لمعرفة سبب الرفض."""
        else:
            user_message = f"""❌ Your payment has been rejected

🆔 Order ID: `{order_id}`
💳 Transaction Number: `{transaction_number}`
📦 Package Type: {order_type}

📞 Please contact admin to know the reason for rejection."""
        
        await context.bot.send_message(user_id, user_message, parse_mode='Markdown')
        
        # رسالة للأدمن مع رقم المعاملة ونوع البروكسي
        proxy_type_ar = "بروكسي ستاتيك" if order_type == "static" else "بروكسي سوكس" if order_type == "socks" else order_type
        
        admin_message = f"""❌ تم رفض الدفع للطلب

🆔 معرف الطلب: `{order_id}`
💳 رقم المعاملة: `{transaction_number}`
👤 معرف المستخدم: `{user_id}`
📝 الطلب: {proxy_type_ar}

📋 تم نقل الطلب إلى الطلبات الفاشلة.

💬 هل تريد إرسال رسالة مخصصة للمستخدم؟"""
    
    keyboard = [
        [InlineKeyboardButton("نعم", callback_data="send_custom_message")],
        [InlineKeyboardButton("لا", callback_data="no_custom_message")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        admin_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return CUSTOM_MESSAGE

async def handle_admin_menu_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إجراءات لوحة الأدمن"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "manage_orders":
        keyboard = [
            [InlineKeyboardButton("الطلبات المعلقة", callback_data="show_pending_orders")],
            [InlineKeyboardButton("حذف الطلبات الفاشلة", callback_data="delete_failed_orders")],
            [InlineKeyboardButton("حذف الطلبات المكتملة", callback_data="delete_completed_orders")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("إدارة الطلبات:", reply_markup=reply_markup)
    
    elif query.data == "show_pending_orders":
        pending_orders = db.get_pending_orders()
        if not pending_orders:
            await query.edit_message_text("لا توجد طلبات معلقة حالياً.")
            return
        
        message = "الطلبات المعلقة:\n\n"
        for order in pending_orders[:10]:  # عرض أول 10 طلبات
            message += f"🔸 معرف: {order[0]}\n"
            message += f"   نوع: {order[2]}\n"
            message += f"   الدولة: {order[3]}\n\n"
        
        await query.edit_message_text(message)
    
    elif query.data == "admin_referrals":
        await show_admin_referrals(query, context)
    
    elif query.data == "user_lookup":
        context.user_data['lookup_action'] = 'lookup'
        await query.edit_message_text("يرجى إرسال معرف المستخدم أو @username للبحث:")
        return USER_LOOKUP

async def show_admin_referrals(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات الإحالات للأدمن"""
    # إحصائيات الإحالات
    total_referrals = db.execute_query("SELECT COUNT(*) FROM referrals")[0][0]
    total_amount = db.execute_query("SELECT SUM(amount) FROM referrals")[0][0] or 0
    
    # أفضل المحيلين
    top_referrers = db.execute_query('''
        SELECT u.first_name, u.last_name, COUNT(r.id) as referral_count, SUM(r.amount) as total_earned
        FROM users u
        JOIN referrals r ON u.user_id = r.referrer_id
        GROUP BY u.user_id
        ORDER BY referral_count DESC
        LIMIT 5
    ''')
    
    message = f"📊 إحصائيات الإحالات\n\n"
    message += f"إجمالي الإحالات: {total_referrals}\n"
    message += f"إجمالي المبلغ: {total_amount:.2f}$\n\n"
    message += "أفضل المحيلين:\n"
    
    for i, referrer in enumerate(top_referrers, 1):
        message += f"{i}. {referrer[0]} {referrer[1]}: {referrer[2]} إحالة ({referrer[3]:.2f}$)\n"
    
    keyboard = [
        [InlineKeyboardButton("تحديد قيمة الإحالة", callback_data="set_referral_amount")],
        [InlineKeyboardButton("تصفير رصيد مستخدم", callback_data="reset_user_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def handle_proxy_details_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال تفاصيل البروكسي خطوة بخطوة"""
    query = update.callback_query
    
    if query:
        await query.answer()
        
        if query.data.startswith("proxy_type_"):
            proxy_type = query.data.replace("proxy_type_", "")
            context.user_data['admin_proxy_type'] = proxy_type
            context.user_data['admin_input_state'] = ENTER_PROXY_ADDRESS
            
            await query.edit_message_text("2️⃣ يرجى إدخال عنوان البروكسي:")
            return ENTER_PROXY_ADDRESS
    
    else:
        # معالجة النص المدخل
        text = update.message.text
        current_state = context.user_data.get('admin_input_state', ENTER_PROXY_ADDRESS)
        
        if current_state == ENTER_PROXY_ADDRESS:
            # التحقق من صحة عنوان IP
            if not validate_ip_address(text):
                await update.message.reply_text(
                    "❌ عنوان IP غير صحيح!\n\n"
                    "✅ الشكل المطلوب: xxx.xxx.xxx.xxx\n"
                    "✅ مثال صحيح: 192.168.1.1 أو 62.1.2.1\n"
                    "✅ يُقبل من 1-3 أرقام لكل جزء\n\n"
                    "يرجى إعادة إدخال عنوان IP:"
                )
                return ENTER_PROXY_ADDRESS
            
            context.user_data['admin_proxy_address'] = text
            context.user_data['admin_input_state'] = ENTER_PROXY_PORT
            await update.message.reply_text("3️⃣ يرجى إدخال البورت:")
            return ENTER_PROXY_PORT
        
        elif current_state == ENTER_PROXY_PORT:
            # التحقق من صحة البورت
            if not validate_port(text):
                await update.message.reply_text(
                    "❌ رقم البورت غير صحيح!\n\n"
                    "✅ يجب أن يكون رقماً فقط\n"
                    "✅ حد أقصى 6 أرقام\n"
                    "✅ مثال صحيح: 80, 8080, 123456\n\n"
                    "يرجى إعادة إدخال رقم البورت:"
                )
                return ENTER_PROXY_PORT
            
            context.user_data['admin_proxy_port'] = text
            
            # تحديد نوع البروكسي المختار لعرض الدول المناسبة
            proxy_type = context.user_data.get('admin_proxy_type', 'static')
            if proxy_type == 'socks':
                countries = SOCKS_COUNTRIES['ar']
            else:
                countries = STATIC_COUNTRIES['ar']
            
            # عرض قائمة الدول مقسمة
            reply_markup = create_paginated_keyboard(countries, "admin_country_", 0, 8, 'ar')
            await update.message.reply_text("4️⃣ اختر الدولة:", reply_markup=reply_markup)
            return ENTER_COUNTRY
        
        elif current_state == ENTER_COUNTRY:
            # معالجة إدخال الدولة يدوياً
            context.user_data['admin_proxy_country'] = text
            context.user_data['admin_input_state'] = ENTER_STATE
            await update.message.reply_text("5️⃣ يرجى إدخال اسم الولاية:")
            return ENTER_STATE
        
        elif current_state == ENTER_STATE:
            # معالجة إدخال الولاية يدوياً
            context.user_data['admin_proxy_state'] = text
            context.user_data['admin_input_state'] = ENTER_USERNAME
            await update.message.reply_text("6️⃣ يرجى إدخال اسم المستخدم للبروكسي:")
            return ENTER_USERNAME
        
        elif current_state == ENTER_USERNAME:
            context.user_data['admin_proxy_username'] = text
            context.user_data['admin_input_state'] = ENTER_PASSWORD
            await update.message.reply_text("7️⃣ يرجى إدخال كلمة المرور:")
            return ENTER_PASSWORD
        
        elif current_state == ENTER_PASSWORD:
            context.user_data['admin_proxy_password'] = text
            context.user_data['admin_input_state'] = ENTER_THANK_MESSAGE
            await update.message.reply_text("8️⃣ يرجى إدخال رسالة شكر قصيرة:")
            return ENTER_THANK_MESSAGE
        
        elif current_state == ENTER_THANK_MESSAGE:
            thank_message = text
            context.user_data['admin_thank_message'] = thank_message
            
            # عرض المعلومات للمراجعة قبل الإرسال
            await show_proxy_preview(update, context)
            return ENTER_THANK_MESSAGE
    
    return current_state

async def send_proxy_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, thank_message: str = None) -> None:
    """إرسال تفاصيل البروكسي للمستخدم"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # الحصول على التاريخ والوقت الحاليين
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # إنشاء رسالة البروكسي للمستخدم
        proxy_message = f"""✅ تم معالجة طلب {user_full_name}

🔐 تفاصيل البروكسي:
📡 العنوان: `{context.user_data['admin_proxy_address']}`
🔌 البورت: `{context.user_data['admin_proxy_port']}`
🌍 الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
🏠 الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
👤 اسم المستخدم: `{context.user_data['admin_proxy_username']}`
🔑 كلمة المرور: `{context.user_data['admin_proxy_password']}`

━━━━━━━━━━━━━━━
🆔 معرف الطلب: `{order_id}`
📅 التاريخ: {current_date}
🕐 الوقت: {current_time}

━━━━━━━━━━━━━━━
💬 {thank_message}"""
        
        # إرسال البروكسي للمستخدم
        await context.bot.send_message(user_id, proxy_message, parse_mode='Markdown')
        
        # إرسال إشعار نجاح الطلب
        user_language = get_user_language(user_id)
        await context.bot.send_message(
            user_id,
            MESSAGES[user_language]['order_success']
        )
        
        # تحديث حالة الطلب
        proxy_details = {
            'address': context.user_data['admin_proxy_address'],
            'port': context.user_data['admin_proxy_port'],
            'country': context.user_data.get('admin_proxy_country', ''),
            'state': context.user_data.get('admin_proxy_state', ''),
            'username': context.user_data['admin_proxy_username'],
            'password': context.user_data['admin_proxy_password']
        }
        
        db.execute_query(
            "UPDATE orders SET status = 'completed', processed_at = CURRENT_TIMESTAMP, proxy_details = ? WHERE id = ?",
            (json.dumps(proxy_details), order_id)
        )
        
        # رسالة تأكيد للأدمن
        admin_message = f"""✅ تم معالجة طلب {user_full_name}

🔐 تفاصيل البروكسي المرسلة:
📡 العنوان: `{context.user_data['admin_proxy_address']}`
🔌 البورت: `{context.user_data['admin_proxy_port']}`
🌍 الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
🏠 الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
👤 اسم المستخدم: `{context.user_data['admin_proxy_username']}`
🔑 كلمة المرور: `{context.user_data['admin_proxy_password']}`

━━━━━━━━━━━━━━━
🆔 معرف الطلب: `{order_id}`
📅 التاريخ: {current_date}
🕐 الوقت: {current_time}

━━━━━━━━━━━━━━━
💬 {thank_message}"""

        await update.message.reply_text(admin_message, parse_mode='Markdown')
        
        # تنظيف البيانات المؤقتة
        admin_keys = [k for k in context.user_data.keys() if k.startswith('admin_')]
        for key in admin_keys:
            del context.user_data[key]

async def handle_user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة البحث عن مستخدم"""
    search_term = update.message.text
    
    # البحث بالمعرف أو اسم المستخدم
    if search_term.startswith('@'):
        username = search_term[1:]
        query = "SELECT * FROM users WHERE username = ?"
        user_result = db.execute_query(query, (username,))
    else:
        try:
            user_id = int(search_term)
            query = "SELECT * FROM users WHERE user_id = ?"
            user_result = db.execute_query(query, (user_id,))
        except ValueError:
            await update.message.reply_text("معرف المستخدم غير صحيح!")
            return ConversationHandler.END
    
    if not user_result:
        await update.message.reply_text("المستخدم غير موجود!")
        return ConversationHandler.END
    
    user = user_result[0]
    user_id = user[0]
    
    # إحصائيات المستخدم
    successful_orders = db.execute_query(
        "SELECT COUNT(*), SUM(payment_amount) FROM orders WHERE user_id = ? AND status = 'completed'",
        (user_id,)
    )[0]
    
    failed_orders = db.execute_query(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'failed'",
        (user_id,)
    )[0][0]
    
    pending_orders = db.execute_query(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'pending'",
        (user_id,)
    )[0][0]
    
    referral_count = db.execute_query(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?",
        (user_id,)
    )[0][0]
    
    last_successful_order = db.execute_query(
        "SELECT created_at FROM orders WHERE user_id = ? AND status = 'completed' ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    
    report = f"""📊 تقرير المستخدم

👤 الاسم: {user[2]} {user[3]}
📝 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 المعرف: {user[0]}

━━━━━━━━━━━━━━━
📈 إحصائيات الشراء:
✅ الشراءات الناجحة: {successful_orders[0]}
💰 قيمة الشراءات: {successful_orders[1] or 0:.2f}$
❌ الشراءات الفاشلة: {failed_orders}
⏳ طلبات معلقة: {pending_orders}

━━━━━━━━━━━━━━━
👥 الإحالات:
📊 عدد الإحالات: {referral_count}
💵 رصيد الإحالات: {user[5]:.2f}$

━━━━━━━━━━━━━━━
📅 آخر شراء ناجح: {last_successful_order[0][0] if last_successful_order else 'لا يوجد'}
📅 تاريخ الانضمام: {user[7]}"""
    
    await update.message.reply_text(report)
    return ConversationHandler.END

async def handle_user_lookup_unified(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالج موحد للبحث عن المستخدمين وتصفير الرصيد"""
    # التحقق من السياق لتحديد العملية المطلوبة
    user_data_action = context.user_data.get('lookup_action', 'lookup')
    
    if user_data_action == 'reset_balance':
        return await handle_balance_reset(update, context)
    else:
        return await handle_user_lookup(update, context)

async def handle_admin_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الطلبات للأدمن"""
    keyboard = [
        [KeyboardButton("📋 الطلبات المعلقة")],
        [KeyboardButton("🔍 الاستعلام عن طلب")],
        [KeyboardButton("🗑️ حذف الطلبات الفاشلة"), KeyboardButton("🗑️ حذف الطلبات المكتملة")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📋 إدارة الطلبات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_money_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الأموال للأدمن"""
    keyboard = [
        [KeyboardButton("📊 إحصاء المبيعات")],
        [KeyboardButton("💲 إدارة الأسعار")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 إدارة الأموال\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_referrals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إدارة الإحالات للأدمن"""
    keyboard = [
        [KeyboardButton("💵 تحديد قيمة الإحالة")],
        [KeyboardButton("📊 إحصائيات المستخدمين")],
        [KeyboardButton("🗑️ تصفير رصيد مستخدم")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👥 إدارة الإحالات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة قائمة إعدادات الأدمن"""
    keyboard = [
        [KeyboardButton("🌐 تغيير اللغة")],
        [KeyboardButton("🔐 تغيير كلمة المرور")],
        [KeyboardButton("🔕 ساعات الهدوء")],
        [KeyboardButton("🗃️ إدارة قاعدة البيانات")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚙️ إعدادات الأدمن\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_admin_user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة استعلام عن مستخدم"""
    await update.message.reply_text(
        "🔍 استعلام عن مستخدم\n\nيرجى إرسال:\n- معرف المستخدم (رقم)\n- أو اسم المستخدم (@username)"
    )
    return USER_LOOKUP

async def return_to_user_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة لوضع المستخدم العادي"""
    context.user_data['is_admin'] = False
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء الأزرار الرئيسية للمستخدم
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][3])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        MESSAGES[language]['welcome'],
        reply_markup=reply_markup
    )

async def show_pending_orders_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض الطلبات المعلقة للأدمن"""
    pending_orders = db.get_pending_orders()
    
    if not pending_orders:
        await update.message.reply_text("✅ لا توجد طلبات معلقة حالياً.")
        return
    
    message = "📋 الطلبات المعلقة:\n\n"
    for i, order in enumerate(pending_orders[:10], 1):  # عرض أول 10 طلبات
        message += f"{i}. 🆔 `{order[0]}`\n"
        message += f"   📦 النوع: {order[2]}\n"
        message += f"   🌍 الدولة: {order[3]}\n"
        message += f"   📅 التاريخ: {order[9]}\n\n"
    
    if len(pending_orders) > 10:
        message += f"... و {len(pending_orders) - 10} طلبات أخرى"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def delete_failed_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف الطلبات الفاشلة"""
    result = db.execute_query("DELETE FROM orders WHERE status = 'failed'")
    deleted_count = db.execute_query("SELECT changes()")[0][0]
    
    await update.message.reply_text(f"🗑️ تم حذف {deleted_count} طلب فاشل.")

async def delete_completed_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """حذف الطلبات المكتملة"""
    result = db.execute_query("DELETE FROM orders WHERE status = 'completed'")
    deleted_count = db.execute_query("SELECT changes()")[0][0]
    
    await update.message.reply_text(f"🗑️ تم حذف {deleted_count} طلب مكتمل.")

async def show_sales_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات المبيعات"""
    # إحصائيات المبيعات الناجحة
    stats = db.execute_query("""
        SELECT COUNT(*), SUM(payment_amount) 
        FROM orders 
        WHERE status = 'completed' AND proxy_type != 'withdrawal'
    """)[0]
    
    # إحصائيات السحوبات
    withdrawals = db.execute_query("""
        SELECT COUNT(*), SUM(payment_amount)
        FROM orders 
        WHERE proxy_type = 'withdrawal' AND status = 'completed'
    """)[0]
    
    total_orders = stats[0] or 0
    total_revenue = stats[1] or 0.0
    withdrawal_count = withdrawals[0] or 0
    withdrawal_amount = withdrawals[1] or 0.0
    
    message = f"""📊 إحصائيات المبيعات

💰 المبيعات الناجحة:
📦 عدد الطلبات: {total_orders}
💵 إجمالي الإيرادات: `{total_revenue:.2f}$`

💸 السحوبات:
📋 عدد الطلبات: {withdrawal_count}
💰 إجمالي المسحوب: `{withdrawal_amount:.2f}$`

━━━━━━━━━━━━━━━
📈 صافي الربح: `{total_revenue - withdrawal_amount:.2f}$`"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def database_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة إدارة قاعدة البيانات"""
    keyboard = [
        [KeyboardButton("📊 تحميل قاعدة البيانات")],
        [KeyboardButton("🗑️ تفريغ قاعدة البيانات")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🗃️ إدارة قاعدة البيانات\nاختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def database_export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة تصدير قاعدة البيانات"""
    keyboard = [
        [KeyboardButton("📊 Excel"), KeyboardButton("📄 CSV")],
        [KeyboardButton("🗃️ SQLite Database")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📊 تحميل قاعدة البيانات\nاختر صيغة التصدير:",
        reply_markup=reply_markup
    )

async def return_to_admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية للأدمن"""
    # استخدام الكيبورد الجديد المحدث
    keyboard = [
        [KeyboardButton("📋 إدارة الطلبات")],
        [KeyboardButton("💰 إدارة الأموال"), KeyboardButton("👥 الإحالات")],
        [KeyboardButton("📢 البث"), KeyboardButton("🔍 استعلام عن مستخدم")],
        [KeyboardButton("⚙️ الإعدادات")],
        [KeyboardButton("🚪 تسجيل الخروج")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔧 لوحة الأدمن الرئيسية\nاختر الخدمة المطلوبة:",
        reply_markup=reply_markup
    )

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرسائل النصية"""
    text = update.message.text
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    is_admin = context.user_data.get('is_admin', False)
    
    # معالجة الإدخال اليدوي للدول والولايات
    waiting_for = context.user_data.get('waiting_for')
    if waiting_for == 'manual_country':
        context.user_data['selected_country'] = text
        context.user_data.pop('waiting_for', None)
        await update.message.reply_text(f"تم اختيار الدولة: {text}\nيرجى إدخال اسم المنطقة/الولاية:")
        context.user_data['waiting_for'] = 'manual_state'
        return
    
    elif waiting_for == 'manual_state':
        context.user_data['selected_state'] = text
        context.user_data.pop('waiting_for', None)
        await update.message.reply_text(f"تم اختيار المنطقة: {text}")
        
        # الانتقال لطرق الدفع
        keyboard = [
            [InlineKeyboardButton("💳 شام كاش", callback_data="payment_shamcash")],
            [InlineKeyboardButton("💳 سيرياتيل كاش", callback_data="payment_syriatel")],
            [InlineKeyboardButton("🪙 Coinex", callback_data="payment_coinex")],
            [InlineKeyboardButton("🪙 Binance", callback_data="payment_binance")],
            [InlineKeyboardButton("🪙 Payeer", callback_data="payment_payeer")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            MESSAGES[language]['payment_methods'],
            reply_markup=reply_markup
        )
        return
    
    # أزرار الأدمن
    if is_admin:
        # القوائم الرئيسية للأدمن
        if text == "📋 إدارة الطلبات":
            await handle_admin_orders_menu(update, context)
        elif text == "💰 إدارة الأموال":
            await handle_admin_money_menu(update, context)
        elif text == "👥 الإحالات":
            await handle_admin_referrals_menu(update, context)
        elif text == "⚙️ الإعدادات":
            await handle_admin_settings_menu(update, context)
        # تم نقل معالجة الاستعلام عن مستخدم إلى admin_functions_conv_handler
        elif text == "🚪 تسجيل الخروج":
            await admin_logout_confirmation(update, context)
        
        # إدارة الطلبات
        elif text == "📋 الطلبات المعلقة":
            await show_pending_orders_admin(update, context)
        # تم نقل معالجة الاستعلام عن طلب إلى admin_functions_conv_handler
        elif text == "🗑️ حذف الطلبات الفاشلة":
            await delete_failed_orders(update, context)
        elif text == "🗑️ حذف الطلبات المكتملة":
            await delete_completed_orders(update, context)
        
        # إدارة الأموال
        elif text == "📊 إحصاء المبيعات":
            await show_sales_statistics(update, context)
        elif text == "💲 إدارة الأسعار":
            await manage_prices_menu(update, context)
        # تم نقل معالجة تعديل الأسعار إلى admin_functions_conv_handler
        
        # إدارة الإحالات
        # تم نقل معالجة تحديد قيمة الإحالة إلى admin_functions_conv_handler
        elif text == "📊 إحصائيات المستخدمين":
            await show_user_statistics(update, context)
        # تم نقل معالجة تصفير رصيد مستخدم إلى admin_functions_conv_handler
        
        # إعدادات الأدمن
        elif text == "🌐 تغيير اللغة":
            await handle_settings(update, context)
        elif text == "🔐 تغيير كلمة المرور":
            await change_admin_password(update, context)
        # تم نقل معالجة ساعات الهدوء إلى admin_functions_conv_handler
        elif text == "🗃️ إدارة قاعدة البيانات":
            await database_management_menu(update, context)
        
        # معالجة إدارة قاعدة البيانات
        elif text == "📊 تحميل قاعدة البيانات" and is_admin:
            await database_export_menu(update, context)
        elif text == "🗑️ تفريغ قاعدة البيانات":
            await confirm_database_clear(update, context)
        
        # معالجة تصدير قاعدة البيانات
        elif text == "📊 Excel":
            await export_database_excel(update, context)
        elif text == "📄 CSV":
            await export_database_csv(update, context)
        elif text == "🗃️ SQLite Database":
            await export_database_sqlite(update, context)
        
        # العودة للقائمة الرئيسية
        elif text == "🔙 العودة للقائمة الرئيسية":
            await return_to_admin_main(update, context)
        
        return
    
    # التحقق من الأزرار الرئيسية للمستخدم
    if text == MESSAGES[language]['main_menu_buttons'][0]:  # طلب بروكسي ستاتيك
        await handle_static_proxy_request(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][1]:  # طلب بروكسي سوكس
        await handle_socks_proxy_request(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][2]:  # إحالاتي
        await handle_referrals(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][3]:  # تذكير بطلباتي
        await handle_order_reminder(update, context)
    elif text == MESSAGES[language]['main_menu_buttons'][4]:  # الإعدادات
        await handle_settings(update, context)

# ==== الوظائف المفقودة ====

async def manage_prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """قائمة إدارة الأسعار"""
    keyboard = [
        [KeyboardButton("💰 تعديل أسعار ستاتيك")],
        [KeyboardButton("💰 تعديل أسعار سوكس")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💲 إدارة الأسعار\nاختر نوع البروكسي لتعديل أسعاره:",
        reply_markup=reply_markup
    )

async def set_referral_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد قيمة الإحالة"""
    await update.message.reply_text(
        "💵 تحديد قيمة الإحالة الواحدة\n\nيرجى إرسال قيمة الإحالة بالدولار (مثال: `0.1`):",
        parse_mode='Markdown'
    )
    return REFERRAL_AMOUNT

async def handle_referral_amount_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث قيمة الإحالة"""
    try:
        amount = float(update.message.text)
        
        # حفظ في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("referral_amount", str(amount))
        )
        
        await update.message.reply_text(f"✅ تم تحديث قيمة الإحالة إلى `{amount}$`\n\n📢 سيتم إشعار جميع المستخدمين بالتحديث...", parse_mode='Markdown')
        
        # إشعار جميع المستخدمين بالتحديث
        await broadcast_referral_update(context, amount)
        
    except ValueError:
        await update.message.reply_text("❌ يرجى إرسال رقم صحيح!")
        return REFERRAL_AMOUNT
    
    return ConversationHandler.END

async def set_quiet_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد ساعات الهدوء"""
    # الحصول على الإعداد الحالي
    current_setting = db.execute_query("SELECT value FROM settings WHERE key = 'quiet_hours'")
    current = current_setting[0][0] if current_setting else "24h"
    
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if current == '8_18' else '🔕'} 08:00 - 18:00", callback_data="quiet_8_18")],
        [InlineKeyboardButton(f"{'✅' if current == '22_6' else '🔕'} 22:00 - 06:00", callback_data="quiet_22_6")],
        [InlineKeyboardButton(f"{'✅' if current == '12_14' else '🔕'} 12:00 - 14:00", callback_data="quiet_12_14")],
        [InlineKeyboardButton(f"{'✅' if current == '20_22' else '🔕'} 20:00 - 22:00", callback_data="quiet_20_22")],
        [InlineKeyboardButton(f"{'✅' if current == '24h' else '🔊'} 24 ساعة مع صوت", callback_data="quiet_24h")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔕 ساعات الهدوء\n\nاختر الفترة التي تريد فيها إشعارات صامتة:\n(خارج هذه الفترات ستصل الإشعارات بصوت)",
        reply_markup=reply_markup
    )
    return QUIET_HOURS

async def handle_quiet_hours_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار ساعات الهدوء"""
    query = update.callback_query
    await query.answer()
    
    quiet_period = query.data.replace("quiet_", "")
    
    # حفظ في قاعدة البيانات
    db.execute_query(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("quiet_hours", quiet_period)
    )
    
    if quiet_period == "24h":
        message = "🔊 تم تعيين الإشعارات بصوت لمدة 24 ساعة"
    else:
        start_hour, end_hour = quiet_period.split("_")
        message = f"🔕 تم تعيين ساعات الهدوء: `{start_hour}:00 - {end_hour}:00`"
    
    await query.edit_message_text(message, parse_mode='Markdown')
    return ConversationHandler.END

async def admin_logout_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """طلب تأكيد تسجيل خروج الأدمن"""
    keyboard = [
        [InlineKeyboardButton("✅ نعم، تسجيل الخروج", callback_data="confirm_logout")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_logout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚪 **تأكيد تسجيل الخروج**\n\nهل أنت متأكد من رغبتك في تسجيل الخروج من لوحة الأدمن؟",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_logout_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تأكيد تسجيل الخروج"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_logout":
        # تسجيل الخروج
        context.user_data.pop('is_admin', None)
        
        # إنشاء كيبورد المستخدم العادي
        user_id = update.effective_user.id
        language = get_user_language(user_id)
        
        keyboard = [
            [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
            [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
            [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2])],
            [KeyboardButton(MESSAGES[language]['main_menu_buttons'][3]), 
             KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await query.edit_message_text(
            "✅ **تم تسجيل الخروج بنجاح**\n\n👋 مرحباً بعودتك كمستخدم عادي\nيمكنك الآن استخدام جميع خدمات البوت",
            parse_mode='Markdown'
        )
        
        await context.bot.send_message(
            update.effective_chat.id,
            "🎯 القائمة الرئيسية\nاختر الخدمة المطلوبة:",
            reply_markup=reply_markup
        )
        
    elif query.data == "cancel_logout":
        await query.edit_message_text(
            "❌ **تم إلغاء تسجيل الخروج**\n\n🔧 لا تزال في لوحة الأدمن\nيمكنك المتابعة في استخدام أدوات الإدارة",
            parse_mode='Markdown'
        )

async def handle_back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """العودة للقائمة الرئيسية للأدمن من الأزرار inline"""
    query = update.callback_query
    await query.answer()
    
    # التأكد من أن المستخدم أدمن
    if not context.user_data.get('is_admin', False):
        await query.edit_message_text("❌ هذه الخدمة مخصصة للأدمن فقط!")
        return
    
    # استخدام الكيبورد الجديد المحدث
    keyboard = [
        [KeyboardButton("📋 إدارة الطلبات")],
        [KeyboardButton("💰 إدارة الأموال"), KeyboardButton("👥 الإحالات")],
        [KeyboardButton("📢 البث"), KeyboardButton("🔍 استعلام عن مستخدم")],
        [KeyboardButton("⚙️ الإعدادات")],
        [KeyboardButton("🚪 تسجيل الخروج")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await query.edit_message_text("🔧 **تم العودة للقائمة الرئيسية**")
    
    await context.bot.send_message(
        update.effective_chat.id,
        "🔧 لوحة الأدمن الرئيسية\nاختر الخدمة المطلوبة:",
        reply_markup=reply_markup
    )

async def admin_signout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تسجيل خروج الأدمن (أمر قديم)"""
    context.user_data['is_admin'] = False
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # إنشاء الأزرار الرئيسية للمستخدم
    keyboard = [
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][0])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][1])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][2])],
        [KeyboardButton(MESSAGES[language]['main_menu_buttons'][3]), 
         KeyboardButton(MESSAGES[language]['main_menu_buttons'][4])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👋 تم تسجيل الخروج من لوحة الأدمن\n\n" + MESSAGES[language]['welcome'],
        reply_markup=reply_markup
    )

async def admin_order_inquiry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """الاستعلام عن طلب"""
    await update.message.reply_text(
        "🔍 الاستعلام عن طلب\n\nيرجى إرسال معرف الطلب (`16` خانة):",
        parse_mode='Markdown'
    )
    return ADMIN_ORDER_INQUIRY

async def handle_order_inquiry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة الاستعلام عن طلب"""
    order_id = update.message.text.strip()
    
    # التحقق من صحة معرف الطلب
    if len(order_id) != 16:
        await update.message.reply_text("❌ معرف الطلب يجب أن يكون `16` خانة", parse_mode='Markdown')
        return ADMIN_ORDER_INQUIRY
    
    # البحث عن الطلب
    query = """
        SELECT o.*, u.first_name, u.last_name, u.username 
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    result = db.execute_query(query, (order_id,))
    
    if not result:
        await update.message.reply_text(f"❌ لم يتم العثور على طلب بالمعرف: `{order_id}`", parse_mode='Markdown')
        return ConversationHandler.END
    
    order = result[0]
    status = order[8]  # حالة الطلب
    
    if status == 'pending':
        # إعادة إرسال الطلب مع إثبات الدفع
        await resend_order_notification(update, context, order)
        await update.message.reply_text("✅ تم إعادة إرسال الطلب مع زر المعالجة")
    elif status == 'completed':
        processed_date = order[10] if order[10] else "غير محدد"
        await update.message.reply_text(f"ℹ️ الطلب `{order_id}` تم معالجته بالفعل\n📅 تاريخ المعالجة: {processed_date}", parse_mode='Markdown')
    elif status == 'failed':
        await update.message.reply_text(f"ℹ️ الطلب `{order_id}` فشل ولم يتم معالجته", parse_mode='Markdown')
    
    return ConversationHandler.END

async def resend_order_notification(update: Update, context: ContextTypes.DEFAULT_TYPE, order: tuple) -> None:
    """إعادة إرسال إشعار الطلب"""
    order_id = order[0]
    
    # تحديد طريقة الدفع باللغة العربية
    payment_methods_ar = {
        'shamcash': 'شام كاش',
        'syriatel': 'سيرياتيل كاش',
        'coinex': 'Coinex',
        'binance': 'Binance',
        'payeer': 'Payeer'
    }
    
    payment_method_ar = payment_methods_ar.get(order[5], order[5])
    
    message = f"""🔔 طلب معاد إرساله

👤 الاسم: `{order[12]} {order[13] or ''}`
📱 اسم المستخدم: @{order[14] or 'غير محدد'}
🆔 معرف المستخدم: `{order[1]}`

━━━━━━━━━━━━━━━
📦 تفاصيل الطلب:
🔧 نوع البروكسي: {order[2]}
🌍 الدولة: {order[3]}
🏠 الولاية: {order[4]}

━━━━━━━━━━━━━━━
💳 تفاصيل الدفع:
💰 طريقة الدفع: {payment_method_ar}
📄 إثبات الدفع: {"✅ مرفق" if order[7] else "❌ غير مرفق"}

━━━━━━━━━━━━━━━
🔗 معرف الطلب: `{order_id}`
📅 تاريخ الطلب: {order[9]}
📊 الحالة: ⏳ معلق"""

    keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    main_msg = await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # إرسال إثبات الدفع كرد على رسالة الطلب
    if order[7]:  # payment_proof
        if order[7].startswith("photo:"):
            file_id = order[7].replace("photo:", "")
            await context.bot.send_photo(
                update.effective_chat.id,
                photo=file_id,
                caption=f"📸 إثبات دفع للطلب بمعرف: `{order_id}`",
                parse_mode='Markdown',
                reply_to_message_id=main_msg.message_id
            )
        elif order[7].startswith("text:"):
            text_proof = order[7].replace("text:", "")
            await context.bot.send_message(
                update.effective_chat.id,
                f"📝 إثبات دفع للطلب بمعرف: `{order_id}`\n\nالنص:\n{text_proof}",
                parse_mode='Markdown',
                reply_to_message_id=main_msg.message_id
            )

async def set_static_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار الستاتيك"""
    await update.message.reply_text(
        "💰 تعديل أسعار البروكسي الستاتيك\n\nيرجى إرسال الأسعار بالتنسيق التالي:\n`ISP:3,Verizon:4,ATT:6`\n\nأو إرسال سعر واحد فقط مثل: `5`",
        parse_mode='Markdown'
    )
    return SET_PRICE_STATIC

async def set_socks_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تحديد أسعار السوكس"""
    await update.message.reply_text(
        "💰 تعديل أسعار بروكسي السوكس\n\nيرجى إرسال الأسعار بالتنسيق التالي:\n`5proxy:0.4,10proxy:0.7`\n\nأو إرسال سعر واحد فقط مثل: `0.5`",
        parse_mode='Markdown'
    )
    return SET_PRICE_SOCKS

async def handle_static_price_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث أسعار الستاتيك"""
    prices_text = update.message.text
    
    try:
        # تحليل الأسعار الجديدة
        if "," in prices_text:
            # أسعار متعددة مثل: ISP:3,Verizon:4,ATT:6
            price_parts = prices_text.split(",")
            static_prices = {}
            for part in price_parts:
                if ":" in part:
                    key, value = part.split(":", 1)
                    static_prices[key.strip()] = value.strip()
        else:
            # سعر واحد لجميع الأنواع
            static_prices = {
                "ISP": prices_text.strip(),
                "Verizon": prices_text.strip(), 
                "ATT": prices_text.strip()
            }
        
        # تحديث رسائل الحزم
        new_static_message_ar = f"""📦 Static Package

🔹 الأسعار:
- Static ISP Risk0: `{static_prices.get('ISP', '3')}$`
- Static Residential Verizon: `{static_prices.get('Verizon', '4')}$`  
- Static Residential AT&T: `{static_prices.get('ATT', '6')}$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{{}}`"""

        new_static_message_en = f"""📦 Static Package

🔹 Prices:
- Static ISP Risk0: {static_prices.get('ISP', '3')}$
- Static Residential Verizon: {static_prices.get('Verizon', '4')}$
- Static Residential AT&T: {static_prices.get('ATT', '6')}$

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
  cc849f22d5117db0b8fe5667e6d4b758

- Syriatel Cash:
  55973911
  14227865

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
  sohilskaf123@gmail.com

- Binance:
  1121540155

- Payeer:
  P1114452356

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: {{}}"""

        # تحديث رسائل الحزم باستخدام الدالة المساعدة
        update_static_messages(static_prices)
        
        # حفظ الأسعار في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("static_prices", prices_text)
        )
        
        await update.message.reply_text(f"✅ تم تحديث أسعار البروكسي الستاتيك بنجاح!\n💰 الأسعار الجديدة: `{prices_text}`\n\n📢 سيتم إشعار جميع المستخدمين بالأسعار الجديدة...", parse_mode='Markdown')
        
        # إشعار جميع المستخدمين بالأسعار الجديدة
        await broadcast_price_update(context, "static", static_prices)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تحديث الأسعار: {str(e)}")
    
    return ConversationHandler.END

async def broadcast_price_update(context: ContextTypes.DEFAULT_TYPE, proxy_type: str, prices: dict) -> None:
    """إشعار المستخدمين بتحديث الأسعار"""
    try:
        all_users = db.execute_query("SELECT user_id FROM users")
        success_count = 0
        
        if proxy_type == "static":
            message = f"""📢 **تحديث أسعار البروكسي الستاتيك**

🔹 الأسعار الجديدة:
- Static ISP Risk0: `{prices.get('ISP', '3')}$`
- Static Residential Verizon: `{prices.get('Verizon', '4')}$`
- Static Residential AT&T: `{prices.get('ATT', '6')}$`

📦 يمكنك الآن طلب البروكسي بالأسعار الجديدة!"""
        else:
            message = f"""📢 **تحديث أسعار بروكسي السوكس**

🔹 الأسعار الجديدة:
- باكج 5 بروكسيات مؤقتة: `{prices.get('5proxy', '0.4')}$`
- باكج 10 بروكسيات مؤقتة: `{prices.get('10proxy', '0.7')}$`

📦 يمكنك الآن طلب البروكسي بالأسعار الجديدة!"""
        
        for user_tuple in all_users:
            user_id = user_tuple[0]
            try:
                await context.bot.send_message(user_id, message, parse_mode='Markdown')
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send price update to {user_id}: {e}")
        
        logger.info(f"Price update sent to {success_count} users")
        
    except Exception as e:
        logger.error(f"Error in broadcast_price_update: {e}")

async def handle_socks_price_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تحديث أسعار السوكس"""
    prices_text = update.message.text
    
    try:
        # تحليل الأسعار الجديدة
        if "," in prices_text:
            # أسعار متعددة مثل: 5proxy:0.4,10proxy:0.7
            price_parts = prices_text.split(",")
            socks_prices = {}
            for part in price_parts:
                if ":" in part:
                    key, value = part.split(":", 1)
                    socks_prices[key.strip()] = value.strip()
        else:
            # سعر واحد لجميع الأنواع
            socks_prices = {
                "5proxy": prices_text.strip(),
                "10proxy": str(float(prices_text.strip()) * 1.75)  # 10 بروكسيات أغلى
            }
        
        # تحديث رسائل الحزم
        new_socks_message_ar = f"""📦 Socks Package
كافة دول العالم مع ميزة اختيار الولاية والمزود للبكج

🔹 الأسعار:
- باكج 5 بروكسيات مؤقتة: `{socks_prices.get('5proxy', '0.4')}$`
- باكج 10 بروكسيات مؤقتة: `{socks_prices.get('10proxy', '0.7')}$`

━━━━━━━━━━━━━━━
💳 طرق الدفع المحلية:

- شام كاش:
`cc849f22d5117db0b8fe5667e6d4b758`

- سيرياتيل كاش:
`55973911`
`14227865`

━━━━━━━━━━━━━━━
🪙 طرق الدفع بالعملات الرقمية:

- Coinex:
sohilskaf123@gmail.com

- Binance:
`1121540155`

- Payeer:
`P1114452356`

━━━━━━━━━━━━━━━
📩 الرجاء إرسال إثبات الدفع للبوت مع تفاصيل الطلب
⏱️ يرجى الانتظار حتى تتم معالجة العملية من قبل الأدمن

معرف الطلب: `{{}}`"""

        new_socks_message_en = f"""📦 Socks Package

🔹 Prices:
- 5 Temporary Proxies Package: {socks_prices.get('5proxy', '0.4')}$
- 10 Temporary Proxies Package: {socks_prices.get('10proxy', '0.7')}$

━━━━━━━━━━━━━━━
💳 Local Payment Methods:

- Sham Cash:
  cc849f22d5117db0b8fe5667e6d4b758

- Syriatel Cash:
  55973911
  14227865

━━━━━━━━━━━━━━━
🪙 Cryptocurrency Payment Methods:

- Coinex:
  sohilskaf123@gmail.com

- Binance:
  1121540155

- Payeer:
  P1114452356

━━━━━━━━━━━━━━━
📩 Please send payment proof to the bot with order details
⏱️ Please wait for admin to process manually

Order ID: {{}}"""

        # تحديث رسائل الحزم باستخدام الدالة المساعدة
        update_socks_messages(socks_prices)
        
        # حفظ الأسعار في قاعدة البيانات
        db.execute_query(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("socks_prices", prices_text)
        )
        
        await update.message.reply_text(f"✅ تم تحديث أسعار بروكسي السوكس بنجاح!\n💰 الأسعار الجديدة: `{prices_text}`\n\n📢 سيتم إشعار جميع المستخدمين بالأسعار الجديدة...", parse_mode='Markdown')
        
        # إشعار جميع المستخدمين بالأسعار الجديدة
        await broadcast_price_update(context, "socks", socks_prices)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تحديث الأسعار: {str(e)}")
    
    return ConversationHandler.END

async def reset_user_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """تصفير رصيد مستخدم"""
    context.user_data['lookup_action'] = 'reset_balance'
    await update.message.reply_text(
        "🗑️ تصفير رصيد مستخدم\n\nيرجى إرسال معرف المستخدم أو `@username`:",
        parse_mode='Markdown'
    )
    return USER_LOOKUP

async def handle_balance_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تصفير الرصيد"""
    search_term = update.message.text
    
    # البحث عن المستخدم
    if search_term.startswith('@'):
        username = search_term[1:]
        query = "SELECT * FROM users WHERE username = ?"
        user_result = db.execute_query(query, (username,))
    else:
        try:
            user_id = int(search_term)
            query = "SELECT * FROM users WHERE user_id = ?"
            user_result = db.execute_query(query, (user_id,))
        except ValueError:
            await update.message.reply_text("❌ معرف المستخدم غير صحيح!")
            return ConversationHandler.END
    
    if not user_result:
        await update.message.reply_text("❌ المستخدم غير موجود!")
        return ConversationHandler.END
    
    user = user_result[0]
    user_id = user[0]
    old_balance = user[5]
    
    # تصفير الرصيد
    db.execute_query("UPDATE users SET referral_balance = 0 WHERE user_id = ?", (user_id,))
    
    await update.message.reply_text(
        f"✅ تم تصفير رصيد المستخدم بنجاح!\n\n"
        f"👤 الاسم: `{user[2]} {user[3] or ''}`\n"
        f"💰 الرصيد السابق: `{old_balance:.2f}$`\n"
        f"💰 الرصيد الجديد: `0.00$`",
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END

async def handle_order_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تذكير الطلبات"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # التحقق من آخر استخدام للتذكير
    last_reminder = context.user_data.get('last_reminder', 0)
    current_time = datetime.now().timestamp()
    
    # التحقق من مرور ساعة على آخر استخدام
    if current_time - last_reminder < 3600:  # ساعة واحدة
        remaining_time = int((3600 - (current_time - last_reminder)) / 60)
        await update.message.reply_text(
            f"⏰ يمكنك استخدام التذكير مرة أخرى بعد `{remaining_time}` دقيقة",
            parse_mode='Markdown'
        )
        return
    
    # البحث عن الطلبات المعلقة للمستخدم
    pending_orders = db.execute_query(
        "SELECT id, created_at FROM orders WHERE user_id = ? AND status = 'pending'",
        (user_id,)
    )
    
    if not pending_orders:
        await update.message.reply_text("لا توجد لديك طلبات معلقة حالياً.")
        return
    
    # تحديث وقت آخر استخدام
    context.user_data['last_reminder'] = current_time
    
    # إرسال تذكير للأدمن لكل طلب معلق
    user = db.get_user(user_id)
    
    for order in pending_orders:
        order_id = order[0]
        await send_reminder_to_admin(context, order_id, user)
    
    await update.message.reply_text(
        f"✅ تم إرسال تذكير للأدمن بخصوص `{len(pending_orders)}` طلب معلق",
        parse_mode='Markdown'
    )

async def send_reminder_to_admin(context: ContextTypes.DEFAULT_TYPE, order_id: str, user: tuple) -> None:
    """إرسال تذكير للأدمن"""
    message = f"""🔔 تذكير بطلب معلق
    
👤 الاسم: `{user[2]} {user[3] or ''}`
📱 اسم المستخدم: @{user[1] or 'غير محدد'}
🆔 معرف المستخدم: `{user[0]}`

💬 مرحباً، لدي طلب معلق بانتظار المعالجة

🔗 معرف الطلب: `{order_id}`
📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    keyboard = [[InlineKeyboardButton("🔧 معالجة الطلب", callback_data=f"process_{order_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                ADMIN_CHAT_ID,
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"خطأ في إرسال التذكير: {e}")

async def confirm_database_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تأكيد تفريغ قاعدة البيانات"""
    keyboard = [
        [InlineKeyboardButton("✅ نعم، تفريغ البيانات", callback_data="confirm_clear_db")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_clear_db")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚠️ تحذير!\n\nهل أنت متأكد من تفريغ قاعدة البيانات؟\n\n🗑️ سيتم حذف:\n- جميع الطلبات\n- جميع الإحالات\n- جميع السجلات\n\n✅ سيتم الاحتفاظ ب:\n- بيانات المستخدمين\n- بيانات الأدمن\n- إعدادات النظام",
        reply_markup=reply_markup
    )

async def handle_database_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة تفريغ قاعدة البيانات"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_clear_db":
        try:
            # حذف البيانات مع الاحتفاظ ببيانات المستخدمين والأدمن
            db.execute_query("DELETE FROM orders")
            db.execute_query("DELETE FROM referrals") 
            db.execute_query("DELETE FROM logs")
            
            await query.edit_message_text(
                "✅ تم تفريغ قاعدة البيانات بنجاح!\n\n🗑️ تم حذف:\n- جميع الطلبات\n- جميع الإحالات\n- جميع السجلات\n\n✅ تم الاحتفاظ ببيانات المستخدمين والإعدادات"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ خطأ في تفريغ قاعدة البيانات: {str(e)}")
    
    elif query.data == "cancel_clear_db":
        await query.edit_message_text("❌ تم إلغاء عملية تفريغ قاعدة البيانات")

async def handle_cancel_processing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة إلغاء معالجة الطلب مؤقتاً"""
    query = update.callback_query
    await query.answer()
    
    order_id = context.user_data.get('processing_order_id')
    if order_id:
        # الحصول على بيانات المستخدم
        user_query = "SELECT user_id FROM orders WHERE id = ?"
        user_result = db.execute_query(user_query, (order_id,))
        
        if user_result:
            user_id = user_result[0][0]
            user_language = get_user_language(user_id)
            
            # إرسال رسالة للمستخدم
            if user_language == 'ar':
                message = f"⏸️ تم توقيف معالجة طلبك مؤقتاً رقم `{order_id}`\n\nسيتم استئناف المعالجة لاحقاً من قبل الأدمن."
            else:
                message = f"⏸️ Processing of your order `{order_id}` has been temporarily stopped\n\nProcessing will resume later by admin."
            
            await context.bot.send_message(user_id, message, parse_mode='Markdown')
        
        # رسالة للأدمن
        await query.edit_message_text(
            f"⏸️ تم إلغاء معالجة الطلب مؤقتاً\n\n🆔 معرف الطلب: `{order_id}`\n\n📋 الطلب لا يزال في حالة معلق ويمكن استئناف معالجته لاحقاً",
            parse_mode='Markdown'
        )
        
        # تنظيف البيانات المؤقتة
        context.user_data.pop('processing_order_id', None)
        
    else:
        await query.edit_message_text("❌ لم يتم العثور على طلب لإلغاء معالجته")


async def show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات المستخدمين مرتبة حسب عدد الإحالات"""
    stats_query = """
        SELECT u.first_name, u.last_name, u.username, u.user_id,
               COUNT(r.id) as referral_count, u.referral_balance
        FROM users u
        LEFT JOIN referrals r ON u.user_id = r.referrer_id
        GROUP BY u.user_id
        ORDER BY referral_count DESC
        LIMIT 20
    """
    
    users_stats = db.execute_query(stats_query)
    
    if not users_stats:
        await update.message.reply_text("لا توجد إحصائيات متاحة")
        return
    
    message = "📊 إحصائيات المستخدمين (مرتبة حسب الإحالات)\n\n"
    
    for i, user_stat in enumerate(users_stats, 1):
        name = f"{user_stat[0]} {user_stat[1] or ''}"
        username = f"@{user_stat[2]}" if user_stat[2] else "بدون معرف"
        referral_count = user_stat[4]
        balance = user_stat[5]
        
        message += f"{i}. {name}\n"
        message += f"   👤 {username}\n"
        message += f"   👥 الإحالات: {referral_count}\n"
        message += f"   💰 الرصيد: {balance:.2f}$\n\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

# وظائف التقسيم والتنقل
def paginate_items(items, page=0, items_per_page=8):
    """تقسيم القوائم لصفحات"""
    start = page * items_per_page
    end = start + items_per_page
    return list(items.items())[start:end], len(items) > end

def create_paginated_keyboard(items, callback_prefix, page=0, items_per_page=8, language='ar'):
    """إنشاء كيبورد مقسم بأزرار التنقل"""
    keyboard = []
    
    # إضافة زر "غير ذلك" في المقدمة مع إيموجي مميز
    other_text = "🔧 غير ذلك" if language == 'ar' else "🔧 Other"
    keyboard.append([InlineKeyboardButton(other_text, callback_data=f"{callback_prefix}other")])
    
    # الحصول على العناصر للصفحة الحالية
    page_items, has_more = paginate_items(items, page, items_per_page)
    
    # إضافة عناصر الصفحة الحالية
    for code, name in page_items:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"{callback_prefix}{code}")])
    
    # إضافة أزرار التنقل
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ السابق" if language == 'ar' else "◀️ Previous", 
                                               callback_data=f"{callback_prefix}page_{page-1}"))
    if has_more:
        nav_buttons.append(InlineKeyboardButton("التالي ▶️" if language == 'ar' else "Next ▶️", 
                                               callback_data=f"{callback_prefix}page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def get_states_for_country(country_code):
    """الحصول على قائمة الولايات/المناطق للدولة المحددة"""
    states_map = {
        'US': US_STATES,
        'UK': UK_STATES,
        'DE': DE_STATES,
        'FR': FR_STATES,
        'CA': CA_STATES,
        'AU': AU_STATES,
        'AT': AT_STATES,
        'IT': IT_STATES,
        'ES': ES_STATES,
        'NL': NL_STATES,
        'BE': BE_STATES,
        'CH': CH_STATES,
        'RU': RU_STATES,
        'JP': JP_STATES,
        'BR': BR_STATES,
        'MX': MX_STATES,
        'IN': IN_STATES
    }
    return states_map.get(country_code, None)

async def show_proxy_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض معاينة البروكسي للأدمن قبل الإرسال"""
    order_id = context.user_data['processing_order_id']
    
    # الحصول على معلومات المستخدم والطلب
    user_query = """
        SELECT o.user_id, u.first_name, u.last_name, u.username
        FROM orders o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.id = ?
    """
    user_result = db.execute_query(user_query, (order_id,))
    
    if user_result:
        user_id, first_name, last_name, username = user_result[0]
        user_full_name = f"{first_name} {last_name or ''}".strip()
        
        # الحصول على التاريخ والوقت الحاليين
        from datetime import datetime
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        # إنشاء رسالة المعاينة
        preview_message = f"""📋 مراجعة البروكسي قبل الإرسال

👤 **المستخدم:**
الاسم: {user_full_name}
اسم المستخدم: @{username or 'غير محدد'}
المعرف: `{user_id}`

🔐 **تفاصيل البروكسي:**
العنوان: `{context.user_data['admin_proxy_address']}`
البورت: `{context.user_data['admin_proxy_port']}`
الدولة: {context.user_data.get('admin_proxy_country', 'غير محدد')}
الولاية: {context.user_data.get('admin_proxy_state', 'غير محدد')}
اسم المستخدم: `{context.user_data['admin_proxy_username']}`
كلمة المرور: `{context.user_data['admin_proxy_password']}`

📅 **التاريخ والوقت:**
التاريخ: {current_date}
الوقت: {current_time}

💬 **رسالة الشكر:**
{context.user_data['admin_thank_message']}

━━━━━━━━━━━━━━━
🆔 معرف الطلب: `{order_id}`

هل تريد إرسال هذه المعلومات للمستخدم؟"""

        keyboard = [
            [InlineKeyboardButton("✅ إرسال", callback_data="send_proxy_confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_proxy_send")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(preview_message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض قائمة البث"""
    keyboard = [
        [InlineKeyboardButton("📢 إرسال للجميع", callback_data="broadcast_all")],
        [InlineKeyboardButton("👥 إرسال لمستخدمين مخصصين", callback_data="broadcast_custom")],
        [InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 **قائمة البث**\n\nاختر نوع الإرسال:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_broadcast_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة اختيار نوع البث"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "broadcast_all":
        context.user_data['broadcast_type'] = 'all'
        await query.edit_message_text(
            "📢 **إرسال إعلان للجميع**\n\nيرجى كتابة الرسالة التي تريد إرسالها لجميع المستخدمين:"
        )
        return BROADCAST_MESSAGE
    
    elif query.data == "broadcast_custom":
        context.user_data['broadcast_type'] = 'custom'
        await query.edit_message_text(
            "👥 **إرسال لمستخدمين مخصصين**\n\nيرجى إدخال معرفات المستخدمين أو أسماء المستخدمين:\n\n"
            "**الشكل المطلوب:**\n"
            "• مستخدم واحد: `123456789` أو `@username`\n"
            "• عدة مستخدمين: `123456789 - @user1 - 987654321`\n\n"
            "⚠️ **ملاحظة:** استخدم ` - ` (مسافة قبل وبعد الشرطة) للفصل بين المستخدمين",
            parse_mode='Markdown'
        )
        return BROADCAST_USERS
    
    return ConversationHandler.END

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال رسالة البث"""
    message_text = update.message.text
    context.user_data['broadcast_message'] = message_text
    
    broadcast_type = context.user_data.get('broadcast_type', 'all')
    
    if broadcast_type == 'all':
        # عرض المعاينة للإرسال للجميع
        user_count = db.execute_query("SELECT COUNT(*) FROM users")[0][0]
        
        preview_text = f"""📢 **معاينة الإعلان**

👥 **المستقبلون:** جميع المستخدمين ({user_count} مستخدم)

📝 **الرسالة:**
{message_text}

━━━━━━━━━━━━━━━
هل تريد إرسال هذا الإعلان؟"""

        keyboard = [
            [InlineKeyboardButton("✅ إرسال", callback_data="confirm_broadcast")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(preview_text, reply_markup=reply_markup, parse_mode='Markdown')
        return BROADCAST_CONFIRM
    
    elif broadcast_type == 'custom':
        # للمستخدمين المخصصين - استخدام handle_broadcast_custom_message
        return await handle_broadcast_custom_message(update, context)
    
    return ConversationHandler.END

async def handle_broadcast_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إدخال المستخدمين المخصصين"""
    users_input = update.message.text
    context.user_data['broadcast_users_input'] = users_input
    
    # تحليل المدخلات
    users_list = [user.strip() for user in users_input.split(' - ')]
    valid_users = []
    invalid_users = []
    
    for user in users_list:
        if user.startswith('@'):
            # البحث باسم المستخدم
            username = user[1:]
            user_result = db.execute_query("SELECT user_id, first_name FROM users WHERE username = ?", (username,))
            if user_result:
                valid_users.append((user_result[0][0], user_result[0][1], user))
            else:
                invalid_users.append(user)
        else:
            try:
                # البحث بالمعرف
                user_id = int(user)
                user_result = db.execute_query("SELECT first_name FROM users WHERE user_id = ?", (user_id,))
                if user_result:
                    valid_users.append((user_id, user_result[0][0], user))
                else:
                    invalid_users.append(user)
            except ValueError:
                invalid_users.append(user)
    
    context.user_data['broadcast_valid_users'] = valid_users
    
    if not valid_users:
        await update.message.reply_text("❌ لم يتم العثور على أي مستخدم صحيح. يرجى المحاولة مرة أخرى.")
        return BROADCAST_USERS
    
    # عرض قائمة المستخدمين الصحيحين والخاطئين
    preview_text = f"👥 **المستخدمون المختارون:**\n\n"
    
    if valid_users:
        preview_text += "✅ **مستخدمون صحيحون:**\n"
        for user_id, name, original in valid_users:
            preview_text += f"• {name} ({original})\n"
    
    if invalid_users:
        preview_text += f"\n❌ **مستخدمون غير موجودون:**\n"
        for user in invalid_users:
            preview_text += f"• {user}\n"
    
    preview_text += f"\nيرجى كتابة الرسالة التي تريد إرسالها لـ {len(valid_users)} مستخدم:"
    
    await update.message.reply_text(preview_text, parse_mode='Markdown')
    return BROADCAST_MESSAGE

async def handle_broadcast_custom_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة رسالة البث للمستخدمين المخصصين"""
    message_text = update.message.text
    context.user_data['broadcast_message'] = message_text
    
    valid_users = context.user_data.get('broadcast_valid_users', [])
    
    # عرض المعاينة النهائية
    preview_text = f"""📢 **معاينة الإعلان المخصص**

👥 **المستقبلون:** {len(valid_users)} مستخدم

📝 **الرسالة:**
{message_text}

━━━━━━━━━━━━━━━
هل تريد إرسال هذا الإعلان؟"""

    keyboard = [
        [InlineKeyboardButton("✅ إرسال", callback_data="confirm_broadcast")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(preview_text, reply_markup=reply_markup, parse_mode='Markdown')
    return BROADCAST_CONFIRM

async def handle_broadcast_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة تأكيد أو إلغاء البث"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_broadcast":
        broadcast_type = context.user_data.get('broadcast_type', 'all')
        message_text = context.user_data.get('broadcast_message', '')
        
        await query.edit_message_text("📤 جاري إرسال الإعلان...")
        
        success_count = 0
        failed_count = 0
        
        if broadcast_type == 'all':
            # إرسال للجميع
            all_users = db.execute_query("SELECT user_id FROM users")
            for user_tuple in all_users:
                user_id = user_tuple[0]
                try:
                    await context.bot.send_message(user_id, f"📢 **إعلان هام**\n\n{message_text}", parse_mode='Markdown')
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send broadcast to {user_id}: {e}")
        else:
            # إرسال للمستخدمين المخصصين
            valid_users = context.user_data.get('broadcast_valid_users', [])
            for user_id, name, original in valid_users:
                try:
                    await context.bot.send_message(user_id, f"📢 **إعلان هام**\n\n{message_text}", parse_mode='Markdown')
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send broadcast to {user_id}: {e}")
        
        result_message = f"""✅ **تم إرسال الإعلان**

📊 **الإحصائيات:**
✅ نجح الإرسال: {success_count}
❌ فشل الإرسال: {failed_count}
📊 المجموع: {success_count + failed_count}"""

        await query.edit_message_text(result_message, parse_mode='Markdown')
        
        # تنظيف البيانات المؤقتة
        broadcast_keys = ['broadcast_type', 'broadcast_message', 'broadcast_users_input', 'broadcast_valid_users']
        for key in broadcast_keys:
            context.user_data.pop(key, None)
            
    elif query.data == "cancel_broadcast":
        await query.edit_message_text("❌ تم إلغاء الإعلان.")
        
        # تنظيف البيانات المؤقتة
        broadcast_keys = ['broadcast_type', 'broadcast_message', 'broadcast_users_input', 'broadcast_valid_users']
        for key in broadcast_keys:
            context.user_data.pop(key, None)
    
    return ConversationHandler.END

async def handle_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء عملية البث"""
    # التحقق من صلاحيات الأدمن
    if not context.user_data.get('is_admin', False):
        await update.message.reply_text("❌ هذه الخدمة مخصصة للأدمن فقط!")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("📢 إرسال للجميع", callback_data="broadcast_all")],
        [InlineKeyboardButton("👥 إرسال لمستخدمين مخصصين", callback_data="broadcast_custom")],
        [InlineKeyboardButton("🔙 العودة", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 **قائمة البث**\n\nاختر نوع الإرسال:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return BROADCAST_MESSAGE  # الانتقال لحالة انتظار اختيار نوع البث

def main() -> None:
    """الدالة الرئيسية"""
    if not TOKEN:
        print("يرجى إضافة التوكن في بداية الملف!")
        print("1. اذهب إلى @BotFather على تيليجرام")
        print("2. أنشئ بوت جديد وانسخ التوكن")
        print("3. ضع التوكن في متغير TOKEN في بداية الملف")
        return
    
    # تحميل الأسعار المحفوظة عند بدء التشغيل
    load_saved_prices()
    
    # إنشاء ملفات المساعدة
    create_requirements_file()
    create_readme_file()
    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # معالج تسجيل دخول الأدمن
    # معالج معالجة الطلبات للأدمن
    process_order_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_process_order, pattern="^process_")],
        states={
            PROCESS_ORDER: [
                CallbackQueryHandler(handle_payment_success, pattern="^payment_success$"),
                CallbackQueryHandler(handle_payment_failed, pattern="^payment_failed$")
            ],
            ENTER_PROXY_TYPE: [CallbackQueryHandler(handle_proxy_details_input, pattern="^proxy_type_")],
            ENTER_PROXY_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_PROXY_PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_COUNTRY: [
                CallbackQueryHandler(handle_admin_country_selection, pattern="^admin_country_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)
            ],
            ENTER_STATE: [
                CallbackQueryHandler(handle_admin_country_selection, pattern="^admin_state_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)
            ],
            ENTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            ENTER_THANK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy_details_input)],
            CUSTOM_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_message_input)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )

    # معالج تغيير كلمة المرور
    password_change_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔐 تغيير كلمة المرور$"), change_admin_password)],
        states={
            ADMIN_LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_change)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )

    # معالج شامل لجميع وظائف الأدمن
    admin_functions_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔍 استعلام عن مستخدم$"), handle_admin_user_lookup),
            MessageHandler(filters.Regex("^🗑️ تصفير رصيد مستخدم$"), reset_user_balance),
            MessageHandler(filters.Regex("^💵 تحديد قيمة الإحالة$"), set_referral_amount),
            MessageHandler(filters.Regex("^💰 تعديل أسعار ستاتيك$"), set_static_prices),
            MessageHandler(filters.Regex("^💰 تعديل أسعار سوكس$"), set_socks_prices),
            MessageHandler(filters.Regex("^🔍 الاستعلام عن طلب$"), admin_order_inquiry),
            MessageHandler(filters.Regex("^🔕 ساعات الهدوء$"), set_quiet_hours)
        ],
        states={
            USER_LOOKUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_lookup_unified)],
            REFERRAL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_referral_amount_update)],
            SET_PRICE_STATIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_static_price_update)],
            SET_PRICE_SOCKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_socks_price_update)],
            ADMIN_ORDER_INQUIRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_inquiry)],
            QUIET_HOURS: [CallbackQueryHandler(handle_quiet_hours_selection, pattern="^quiet_")]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )

    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("admin_login", admin_login)],
        states={
            ADMIN_LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_password)],
            ADMIN_MENU: [CallbackQueryHandler(handle_admin_menu_actions)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )
    
    # معالج إثبات الدفع
    payment_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_payment_method_selection, pattern="^payment_")],
        states={
            PAYMENT_PROOF: [MessageHandler(filters.ALL & ~filters.COMMAND, handle_payment_proof)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )
    
    # معالج البث
    broadcast_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📢 البث$"), handle_broadcast_start),
            CallbackQueryHandler(handle_broadcast_selection, pattern="^(broadcast_all|broadcast_custom)$")
        ],
        states={
            BROADCAST_MESSAGE: [
                CallbackQueryHandler(handle_broadcast_selection, pattern="^(broadcast_all|broadcast_custom)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message)
            ],
            BROADCAST_USERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_users)],
            BROADCAST_CONFIRM: [CallbackQueryHandler(handle_broadcast_confirmation, pattern="^(confirm_broadcast|cancel_broadcast)$")],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
    )

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin_signout", admin_signout))
    application.add_handler(admin_conv_handler)
    application.add_handler(password_change_conv_handler)
    application.add_handler(admin_functions_conv_handler)
    application.add_handler(process_order_conv_handler)
    application.add_handler(broadcast_conv_handler)
    application.add_handler(payment_conv_handler)
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    # تشغيل البوت
    print("🚀 بدء تشغيل البوت...")
    print("📊 قاعدة البيانات جاهزة")
    print("⚡ البوت يعمل الآن!")
    print("💡 تأكد من إضافة التوكن للبدء")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()