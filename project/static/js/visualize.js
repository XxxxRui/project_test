// Replace the initial demo data section with this:
let serverHealthData = [];
let timePeriod = 'week';
let tableData = [];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Get data from server
    if (typeof serverData !== 'undefined' && serverData.length > 0) {
        serverHealthData = serverData;
        timePeriod = initialTimePeriod || 'week';
        
        // Use the real data from server for the table
        tableData = serverHealthData.map(item => ({
            date: item.full_date,
            steps: item.steps,
            calories: item.calories,
            sleep: item.sleep
        }));
    } else {
        // If no server data, use demo data for development/testing
        console.log("No server data found, using demo data");
        tableData = generateDailyData();
    }
    
    // Create the initial charts
    createActivityChart();
    createTrendsChart();
    
    // Populate the table
    populateTable();
    
    // Update progress bars
    updateProgressBars();
    
    // Rest of your initialization code...
});

// Then modify createActivityChart() function:
function createActivityChart() {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (activityChart) {
        activityChart.destroy();
    }
    
    // Get data based on selected time period
    const period = document.getElementById('time-period').value;
    let chartData;
    
    if (serverHealthData.length > 0) {
        // Use real data from server
        const labels = serverHealthData.map(item => item.date);
        const steps = serverHealthData.map(item => item.steps);
        const calories = serverHealthData.map(item => item.calories);
        
        chartData = { labels, steps, calories };
    } else {
        // Fallback to demo data
        chartData = demoData[period];
    }
    
    // Create chart with the data...
    activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Steps',
                    data: chartData.steps,
                    // Rest of configuration...
                },
                {
                    label: 'Calories Burned',
                    data: chartData.calories,
                    // Rest of configuration...
                }
            ]
        },
        // Rest of options...
    });
}

// Similarly update createTrendsChart() function:
function createTrendsChart() {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (trendsChart) {
        trendsChart.destroy();
    }
    
    // Get data based on selected time period
    const period = document.getElementById('time-period').value;
    let chartData;
    
    if (serverHealthData.length > 0) {
        // Use real data from server
        const labels = serverHealthData.map(item => item.date);
        const sleep = serverHealthData.map(item => item.sleep);
        
        chartData = { labels, sleep };
    } else {
        // Fallback to demo data
        chartData = demoData[period];
    }
    
    // Create chart with the data...
    trendsChart = new Chart(ctx, {
        // Configuration...
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Sleep (hrs)',
                    data: chartData.sleep,
                    // Rest of configuration...
                }
            ]
        },
        // Rest of options...
    });
}

// Update the time period change handler
function updateCharts() {
    // When time period changes, fetch new data from server
    const newPeriod = document.getElementById('time-period').value;
    
    if (userId) {
        // Make AJAX request to get data for the new time period
        fetch(`/api/health_data?period=${newPeriod}`)
            .then(response => response.json())
            .then(data => {
                serverHealthData = data;
                createActivityChart();
                createTrendsChart();
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                // Fallback to demo data if API call fails
                createActivityChart();
                createTrendsChart();
            });
    } else {
        // No user ID available, just use demo data
        createActivityChart();
        createTrendsChart();
    }
}