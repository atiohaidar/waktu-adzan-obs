import obspython as obs
import urllib.request
import urllib.error
import json
import datetime
# Variabel Global
url = "https://api.aladhan.com/v1/timingsByCity?city=Jakarta&country=Indonesia&method=20"
interval  = 1000
source_names = {
    "Subuh": "Text_Time_Subuh",
    "Dzuhur": "Text_Time_Dzuhur",
    "Ashar": "Text_Time_Ashar",
    "Maghrib": "Text_Time_Maghrib",
    "Isya": "Text_Time_Isya",
    "Hijriah": "Text_Hijriah",
    "TimeNow": "Text_TimeNow",
    "Masehi": "Text_Masehi",
    "Countdown_Adzan_Selanjutnya": "Text_Countdown_Adzan_Selanjutnya",
    "Nama_Adzan_Selanjutnya": "Text_Nama_Adzan_Selanjutnya",
    "Waktu_Adzan_Selanjutnya": "Text_Waktu_Adzan_Selanjutnya",
}
city = "Bandung"
country = "Indonesia"
method = 20 # Metode perhitungan (20 = Kemenag)
adzan_timings = {}
hari_ini = {}
error_value = "Tidak tersedia"
next_adzan = {}

def script_description():
    text = """
    <h1>Jadwal Adzan</h1><br>
    Ini adalah script untuk menampilkan jadwal adzan di OBS<br>
    <a href='https://api.aladhan.com'>API Aladhan</a> (Api yang digunakan pada script ini)<br>
    <a href='https://www.linkedin.com/in/tio-haidar-aa92781a2/' >Linkedin saya</a>
    Code By Tio Haidar Hanif

    """;
    return  text

def script_properties():
    global source_names 
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "country", "Negara", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "city", "Kota", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "method", "Metode Perhitungan", 1, 99, 1)
    obs.obs_properties_add_int(props, "interval", "Interval Refresh Sumber", 1, 100000, 1)
    obs.obs_properties_add_button(props, "refresh_data_adzan", "Refresh", refresh_data_adzan)

    for source_key, source_name in source_names.items():
        #  ini tuh untuk nambah list nya ke property,belum sam aisinya
        property_list = obs.obs_properties_add_list(props, source_key, source_key, obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
        # ini untuk ngambil semua sourcde yang ada di OBS, literaly semuanya
        sources = obs.obs_enum_sources()
        if sources is not None:
            for source in sources:
                tipe_source = obs.obs_source_get_unversioned_id(source)
                if tipe_source in ["text_gdiplus", "text_ft2_source"]: # yang muncul cuman tipe nya ini doang, ga semuanya
                    #  ini ngambil nama source nya
                    name = obs.obs_source_get_name(source)
                    #  ini untuk nambah string (value) ke dalem list nya
                    obs.obs_property_list_add_string(property_list, name, name)
            obs.source_list_release(sources)
    obs.obs_properties_add_button(props, "generate_source_adzan", "Generate Source", generate_source_adzan)
    return props

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "country", country)
    obs.obs_data_set_default_string(settings, "city", city)
    obs.obs_data_set_default_int(settings, "method", method)
    obs.obs_data_set_default_int(settings, "interval", interval)
    # for source_key in source_names.keys():
        # obs.obs_data_set_default_string(settings, source_names[source_key], source_names[source_key])
    
def script_update(settings):
    global country, city, method, interval, source_names
    country = obs.obs_data_get_string(settings, "country")
    city = obs.obs_data_get_string(settings, "city")
    method = obs.obs_data_get_int(settings, "method")
    interval = obs.obs_data_get_int(settings, "interval")
    for source_key, source_name in source_names.items():
        print(f"source_key: {source_key}, source_name: {source_name}")
        source_names[source_key] = obs.obs_data_get_string(settings, source_key)
    obs.timer_remove(update_adzan_text)
    obs.timer_remove(update_adzan_time)
    if any(source_names.values()):
        obs.timer_add(update_adzan_text, interval * 1000)
        obs.timer_add(update_adzan_time, 1000)

def refresh_data_adzan(props, prop):
    update_adzan_text()

def generate_source_adzan(props, prop):
    # ubah nama text button menjadi "Loading..."
    # obs.obs_property_set_enabled(prop, False)
    for source_key, source_name in source_names.items():
        update_property_value(source_key, source_name, props)
        source = obs.obs_get_source_by_name(source_name)
        if source:
            settings = obs.obs_source_get_settings(source)
            obs.obs_data_set_string(settings, "text", "Loading...")
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)
        else:
            add_text_source_in_current_scene(source_name, source_key)


def add_text_source_in_current_scene(source_name, source_key):
    current_scene = obs.obs_frontend_get_current_scene()
    if current_scene is None:
        print("tidak ada scene yang aktif")
        return
    scene = obs.obs_scene_from_source(current_scene)
    obs.obs_source_release(current_scene)
    if scene is None:
        print("scene tidak ditemukan")
        return
    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "text", source_key)
    source = obs.obs_source_create("text_gdiplus", source_name, settings, None)
    if source is None:
        print("gagal membuat source")
        return
    
    obs.obs_scene_add(scene, source)
    obs.obs_source_update(source, settings)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)
    print(f"source '{source_name}' berhasil ditambahkan")


def update_property_value(source_key, source_name, props):  
    # belum berrfungsi  
    settings = obs.obs_data_create()  # Buat data settings
    obs.obs_data_set_string(settings, source_key, source_name)  # Set nilai property
    obs.obs_properties_apply_settings(props, settings)  # Terapkan perubahan ke UI
    obs.obs_data_release(settings)  # Bersihkan data settings

def fetch_data_adzan():
    global url, city, country, method, hari_ini, adzan_timings
    # jika hari ini lebih dari waktu isya, maka ambil data esok hari
    if datetime.datetime.now().time() > datetime.datetime.strptime(adzan_timings.get("Isha", "23:59"), "%H:%M").time():
        # Ambil tanggal hari ini
        today = datetime.date.today()

# Tambah 1 hari untuk mendapatkan tanggal besok
        tomorrow = today + datetime.timedelta(days=1)

# Format ke "dd-mm-yyyy"
        tanggal_besok = tomorrow.strftime("%d-%m-%Y")
        print("Make nya di tanggal")
        url = f"https://api.aladhan.com/v1/timingsByCity/{tanggal_besok}?city={city}&country={country}&method={method}"
    else:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}"
    try:
        # with itu untuk membuka file, dan otomatis menutupnya ketika sudah selesai
        with urllib.request.urlopen(url) as response:
            data = response.read()
            result = json.loads(data)
            hari_ini["hijriah"] = result["data"]["date"]["hijri"]["day"] + " " + result["data"]["date"]["hijri"]["month"]["en"] + " " + result["data"]["date"]["hijri"]["year"]
            hari_ini["masehi"] = datetime.datetime.strptime(result["data"]["date"]["readable"], "%d %b %Y").strftime("%d %b %Y")
            adzan_timings = result["data"]["timings"]
            print("Data jadwal adzan berhasil diambil dari API.\n" + url)
    except urllib.error.URLError as err:
        obs.script_log(obs.LOG_WARNING, f"Error opening URL '{url}': {err.reason}")
        obs.remove_current_callback()


def get_next_adzan():
# kalo adzan nya udah lewat semua (misal abis isya, itu tuh mending langsung cek hari ini)
    global adzan_timings, next_adzan
    now = datetime.datetime.now().time()
    #  default nya di set di waktu subuh
    next_adzan_name = "Fajr"
    next_adzan_time = datetime.datetime.strptime(adzan_timings.get("Fajr", "23:59"), "%H:%M").time()
    for name, time_str in adzan_timings.items():
        if name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            adzan_time = datetime.datetime.strptime(time_str, "%H:%M").time()
            if adzan_time > now:
                # karena udah urut, jadi langsung aja ini nilai nya
                print("adzan_time", adzan_time, "now", now, "next_adzan_time", next_adzan_time)
                    #  mencari nilai terkecil dari waktu adzan
                next_adzan_time = adzan_time
                next_adzan_name = name
                break

    next_adzan = {
        "name": next_adzan_name,
        "time": next_adzan_time
    }
    print(adzan_timings , next_adzan)
def update_adzan_text():
    global adzan_timings, source_names, hari_ini, next_adzan
    fetch_data_adzan()
    get_next_adzan()
    sources = {
        "Subuh": adzan_timings.get("Fajr", error_value),
        "Dzuhur": adzan_timings.get("Dhuhr", error_value),
        "Ashar": adzan_timings.get("Asr", error_value),
        "Maghrib": adzan_timings.get("Maghrib", error_value),
        "Isya": adzan_timings.get("Isha", error_value),
        "Hijriah": hari_ini.get("hijriah", error_value),
        "Masehi": hari_ini.get("masehi",error_value) ,
    }
    if next_adzan and next_adzan.get("name") and next_adzan.get("time"):
        sources["Nama_Adzan_Selanjutnya"] = next_adzan["name"]
        sources["Waktu_Adzan_Selanjutnya"] = next_adzan["time"].strftime("%H:%M")
      
    for source_key, source_name in source_names.items():
        source = obs.obs_get_source_by_name(source_name)
        if source and source_key in sources:
            settings = obs.obs_source_get_settings(source)
            # karena bakal di looping terus, jadi yang datanya ga di olah disini jadi loading aja
            obs.obs_data_set_string(settings, "text", sources.get(source_key, "Loading..."))
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)

def update_adzan_time():
    global adzan_timings, source_names, next_adzan
    countdown = get_countdown(next_adzan.get("time")) if next_adzan.get("time") else "Tidak ada"
    sources = {
        "TimeNow": datetime.datetime.now().strftime("%H:%M:%S"),
        "Countdown_Adzan_Selanjutnya": countdown,
       
    }
    for source_key, source_name in source_names.items():
        source = obs.obs_get_source_by_name(source_name)
        if source and source_key in sources:
            settings = obs.obs_source_get_settings(source)
            try:
                obs.obs_data_set_string(settings, "text", sources.get(source_key, "Loading..."))
            except:
                print("error", source_key)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)

def get_countdown(next_time):
    now = datetime.datetime.now().time()
    now_datetime = datetime.datetime.combine(datetime.date.today(), now)
    next_datetime = datetime.datetime.combine(datetime.date.today(), next_time)

    if next_datetime < now_datetime:
        next_datetime += datetime.timedelta(days=1)

    delta = next_datetime - now_datetime
    if delta < datetime.timedelta(milliseconds=0):
        return "Adzan sudah lewat"
        
    return str(delta).split(".")[0]  # Hapus milidetik