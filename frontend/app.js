// API Configuration
const API_BASE_URL = 'http://localhost:8001';
const DEFAULT_LOCATION = { lat: 52.2297, lon: 21.0122, name: 'Warszawa' };

// Route type configuration
const routeTypes = {
    road: { 
        label: 'Szosowa', 
        icon: 'bike',
        desc: 'Wysoka wrażliwość na wiatr i deszcz'
    },
    mtb: { 
        label: 'MTB', 
        icon: 'mountain',
        desc: 'Toleruje błoto i lekki deszcz'
    },
    city: { 
        label: 'Miejska', 
        icon: 'map-pin',
        desc: 'Krótkie trasy, najbardziej wybaczająca'
    }
};

// Weather code mapping
const weatherCodes = {
    0: { icon: 'sun', label: 'Czyste niebo' },
    1: { icon: 'cloud-sun', label: 'Pogodnie' },
    2: { icon: 'cloud-sun', label: 'Częściowo zachmurzone' },
    3: { icon: 'cloud', label: 'Zachmurzone' },
    45: { icon: 'cloud-fog', label: 'Mgła' },
    48: { icon: 'cloud-fog', label: 'Mgła z szronem' },
    51: { icon: 'cloud-drizzle', label: 'Lekka mżawka' },
    53: { icon: 'cloud-drizzle', label: 'Umiarkowana mżawka' },
    55: { icon: 'cloud-drizzle', label: 'Gęsta mżawka' },
    61: { icon: 'cloud-rain', label: 'Lekki deszcz' },
    63: { icon: 'cloud-rain', label: 'Umiarkowany deszcz' },
    65: { icon: 'cloud-rain', label: 'Silny deszcz' },
    71: { icon: 'snowflake', label: 'Lekki śnieg' },
    73: { icon: 'snowflake', label: 'Umiarkowany śnieg' },
    75: { icon: 'snowflake', label: 'Silny śnieg' },
    77: { icon: 'snowflake', label: 'Ziarna śniegu' },
    80: { icon: 'cloud-rain', label: 'Przelotne opady' },
    81: { icon: 'cloud-rain', label: 'Umiarkowane przelotne' },
    82: { icon: 'cloud-lightning', label: 'Silne przelotne' },
    85: { icon: 'snowflake', label: 'Przelotne opady śniegu' },
    86: { icon: 'snowflake', label: 'Silne opady śniegu' },
    95: { icon: 'cloud-lightning', label: 'Burza' },
    96: { icon: 'cloud-lightning', label: 'Burza z gradem' },
    99: { icon: 'cloud-lightning', label: 'Silna burza' },
};

const conditionLabels = {
    excellent: { text: 'Świetna', color: 'text-green-500', bg: 'score-excellent' },
    good: { text: 'Dobra', color: 'text-lime-500', bg: 'score-good' },
    moderate: { text: 'Średnia', color: 'text-amber-500', bg: 'score-moderate' },
    poor: { text: 'Słaba', color: 'text-orange-500', bg: 'score-poor' },
    bad: { text: 'Zła', color: 'text-red-500', bg: 'score-bad' },
};

// State
let currentLocation = DEFAULT_LOCATION;
let currentRouteType = 'road';
let weatherData = null;

// DOM Elements
const locationBtn = document.getElementById('locationBtn');
const themeToggle = document.getElementById('themeToggle');
const locationInfo = document.getElementById('locationInfo');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const retryBtn = document.getElementById('retryBtn');
const dashboard = document.getElementById('dashboard');
const daysGrid = document.getElementById('daysGrid');
const detailsModal = document.getElementById('detailsModal');
const modalContent = document.getElementById('modalContent');

// Initialize
async function init() {
    lucide.createIcons();
    setupEventListeners();
    renderRouteTypeSelector();
    
    // Try to get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                currentLocation = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    name: 'Twoja lokalizacja'
                };
                loadWeather();
            },
            () => {
                // Use default location on error
                loadWeather();
            }
        );
    } else {
        loadWeather();
    }
}

function setupEventListeners() {
    locationBtn.addEventListener('click', requestLocation);
    themeToggle.addEventListener('click', toggleTheme);
    retryBtn.addEventListener('click', loadWeather);
    detailsModal.addEventListener('click', (e) => {
        if (e.target === detailsModal) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

function renderRouteTypeSelector() {
    const header = document.querySelector('header .container');
    
    const routeSelector = document.createElement('div');
    routeSelector.className = 'mt-4 flex flex-wrap gap-2';
    routeSelector.innerHTML = Object.entries(routeTypes).map(([key, config]) => `
        <button 
            onclick="selectRouteType('${key}')"
            class="route-type-btn flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                currentRouteType === key 
                    ? 'bg-white text-purple-700 font-semibold' 
                    : 'bg-white/20 text-white hover:bg-white/30'
            }"
            data-route="${key}"
        >
            <i data-lucide="${config.icon}" class="w-4 h-4"></i>
            <span>${config.label}</span>
        </button>
    `).join('');
    
    header.appendChild(routeSelector);
    lucide.createIcons();
}

function selectRouteType(type) {
    currentRouteType = type;
    
    // Update UI
    document.querySelectorAll('.route-type-btn').forEach(btn => {
        if (btn.dataset.route === type) {
            btn.className = 'route-type-btn flex items-center gap-2 px-4 py-2 rounded-lg transition bg-white text-purple-700 font-semibold';
        } else {
            btn.className = 'route-type-btn flex items-center gap-2 px-4 py-2 rounded-lg transition bg-white/20 text-white hover:bg-white/30';
        }
    });
    
    // Reload weather with new route type
    if (weatherData) {
        loadWeather();
    }
}

function requestLocation() {
    if (!navigator.geolocation) {
        showError('Geolokalizacja nie jest wspierana w tej przeglądarce');
        return;
    }
    
    locationBtn.disabled = true;
    locationBtn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i>';
    lucide.createIcons();
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            currentLocation = {
                lat: position.coords.latitude,
                lon: position.coords.longitude,
                name: 'Twoja lokalizacja'
            };
            locationBtn.disabled = false;
            locationBtn.innerHTML = '<i data-lucide="map-pin" class="w-5 h-5"></i><span class="hidden sm:inline">Moja lokalizacja</span>';
            lucide.createIcons();
            loadWeather();
        },
        (error) => {
            locationBtn.disabled = false;
            locationBtn.innerHTML = '<i data-lucide="map-pin" class="w-5 h-5"></i><span class="hidden sm:inline">Moja lokalizacja</span>';
            lucide.createIcons();
            showError('Nie udało się pobrać lokalizacji. Sprawdź uprawnienia.');
        }
    );
}

function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
}

// Check saved theme
if (localStorage.getItem('theme') === 'light') {
    document.documentElement.classList.remove('dark');
}

async function loadWeather() {
    showLoading();
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/weather?latitude=${currentLocation.lat}&longitude=${currentLocation.lon}&route_type=${currentRouteType}`
        );
        
        if (!response.ok) {
            throw new Error('Błąd pobierania danych');
        }
        
        weatherData = await response.json();
        renderDashboard();
    } catch (error) {
        showError(error.message);
    }
}

function showLoading() {
    locationInfo.classList.add('hidden');
    dashboard.classList.add('hidden');
    errorState.classList.add('hidden');
    loadingState.classList.remove('hidden');
}

function showError(message) {
    loadingState.classList.add('hidden');
    dashboard.classList.add('hidden');
    errorState.classList.remove('hidden');
    errorMessage.textContent = message;
}

function renderDashboard() {
    loadingState.classList.add('hidden');
    errorState.classList.add('hidden');
    dashboard.classList.remove('hidden');
    
    const routeConfig = routeTypes[currentRouteType];
    
    locationInfo.innerHTML = `
        <p class="text-lg text-gray-700 dark:text-gray-300">
            <i data-lucide="map-pin" class="w-5 h-5 inline mr-1"></i>
            ${currentLocation.name}
        </p>
        <p class="text-sm text-gray-500">
            Tryb: <span class="font-semibold">${routeConfig.label}</span> - ${routeConfig.desc}
        </p>
    `;
    locationInfo.classList.remove('hidden');
    
    daysGrid.innerHTML = weatherData.days.map((day, index) => createDayCard(day, index)).join('');
    
    // Add click handlers
    document.querySelectorAll('.day-card').forEach((card, index) => {
        card.addEventListener('click', () => showDayDetails(weatherData.days[index]));
    });
    
    lucide.createIcons();
}

function createDayCard(day, index) {
    const date = new Date(day.date);
    const today = new Date();
    const isToday = date.toDateString() === today.toDateString();
    const weatherInfo = weatherCodes[day.weather_code] || weatherCodes[0];
    const condition = conditionLabels[day.bike_condition];
    
    return `
        <div class="day-card bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 cursor-pointer card-hover transition-all duration-300 ${isToday ? 'ring-2 ring-primary' : ''}" style="animation-delay: ${index * 0.1}s">
            <div class="text-center mb-3">
                <p class="text-sm text-gray-500 dark:text-gray-400">${day.weekday}</p>
                <p class="text-xs text-gray-400">${day.date}</p>
                ${isToday ? '<span class="text-xs bg-primary text-white px-2 py-0.5 rounded-full">Dziś</span>' : ''}
            </div>
            
            <div class="flex justify-center mb-3">
                <i data-lucide="${weatherInfo.icon}" class="w-12 h-12 text-gray-600 dark:text-gray-300"></i>
            </div>
            
            <div class="text-center mb-3">
                <span class="text-2xl font-bold ${condition.color}">${day.bike_score}</span>
                <span class="text-xs text-gray-400">/100</span>
            </div>
            
            <div class="${condition.bg} text-white text-center py-2 rounded-lg">
                <span class="font-semibold text-sm">${condition.text}</span>
            </div>
            
            <div class="mt-3 text-xs text-gray-500 dark:text-gray-400 text-center">
                <span class="inline-flex items-center gap-1">
                    <i data-lucide="thermometer" class="w-3 h-3"></i>
                    ${Math.round(day.temperature_avg)}°C
                </span>
            </div>
        </div>
    `;
}

function showDayDetails(day) {
    const weatherInfo = weatherCodes[day.weather_code] || weatherCodes[0];
    const condition = conditionLabels[day.bike_condition];
    const routeConfig = routeTypes[currentRouteType];
    
    modalContent.innerHTML = `
        <div class="p-6">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-2xl font-bold text-gray-800 dark:text-white">${day.weekday}</h3>
                    <p class="text-gray-500 dark:text-gray-400">${day.date}</p>
                </div>
                <button onclick="closeModal()" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
                    <i data-lucide="x" class="w-5 h-5 text-gray-500"></i>
                </button>
            </div>
            
            <div class="flex items-center gap-2 mb-4 text-sm text-purple-600 dark:text-purple-400">
                <i data-lucide="${routeConfig.icon}" class="w-4 h-4"></i>
                <span>Tryb: ${routeConfig.label}</span>
            </div>
            
            <div class="flex items-center gap-4 mb-6">
                <i data-lucide="${weatherInfo.icon}" class="w-16 h-16 text-gray-600 dark:text-gray-300"></i>
                <div>
                    <p class="text-lg text-gray-700 dark:text-gray-300">${weatherInfo.label}</p>
                    <div class="flex items-center gap-2">
                        <span class="text-3xl font-bold ${condition.color}">${day.bike_score}</span>
                        <span class="text-gray-400">/100</span>
                    </div>
                </div>
            </div>
            
            <div class="${condition.bg} text-white p-4 rounded-xl mb-6">
                <p class="font-semibold text-lg text-center">${condition.text}</p>
                <p class="text-center text-white/80 text-sm mt-1">${day.recommendation}</p>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <div class="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-1">
                        <i data-lucide="thermometer" class="w-4 h-4"></i>
                        <span class="text-sm">Temperatura</span>
                    </div>
                    <p class="text-xl font-semibold text-gray-800 dark:text-white">
                        ${Math.round(day.temperature_min)}° - ${Math.round(day.temperature_max)}°C
                    </p>
                    <p class="text-xs text-gray-500">Średnia: ${Math.round(day.temperature_avg)}°C</p>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <div class="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-1">
                        <i data-lucide="wind" class="w-4 h-4"></i>
                        <span class="text-sm">Wiatr</span>
                    </div>
                    <p class="text-xl font-semibold text-gray-800 dark:text-white">
                        ${Math.round(day.wind_speed_max)} km/h
                    </p>
                    <p class="text-xs text-gray-500">Średnia: ${Math.round(day.wind_speed_avg)} km/h</p>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <div class="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-1">
                        <i data-lucide="cloud-rain" class="w-4 h-4"></i>
                        <span class="text-sm">Opady</span>
                    </div>
                    <p class="text-xl font-semibold text-gray-800 dark:text-white">
                        ${Math.round(day.precipitation_probability)}%
                    </p>
                    <p class="text-xs text-gray-500">${day.precipitation_sum.toFixed(1)} mm</p>
                </div>
                
                <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                    <div class="flex items-center gap-2 text-gray-500 dark:text-gray-400 mb-1">
                        <i data-lucide="${routeConfig.icon}" class="w-4 h-4"></i>
                        <span class="text-sm">Na ${routeConfig.label.toLowerCase()}</span>
                    </div>
                    <p class="text-xl font-semibold ${condition.color}">${condition.text}</p>
                    <p class="text-xs text-gray-500">Ocena ${day.bike_score}/100</p>
                </div>
            </div>
        </div>
    `;
    
    detailsModal.classList.remove('hidden');
    lucide.createIcons();
}

function closeModal() {
    detailsModal.classList.add('hidden');
}

// Initialize app
init();