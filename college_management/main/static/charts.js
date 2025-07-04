document.addEventListener("DOMContentLoaded", function () {
    const ctx1 = document.getElementById('studentPie').getContext('2d');
    const ctx2 = document.getElementById('teacherPie').getContext('2d');

    new Chart(ctx1, {
        type: 'pie',
        data: {
            labels: studentData.map(d => d.department),
            datasets: [{
                label: 'Students per Department',
                data: studentData.map(d => d.count),
                backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc']
            }]
        }
    });

    new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: teacherData.map(d => d.department),
            datasets: [{
                label: 'Teachers per Department',
                data: teacherData.map(d => d.count),
                backgroundColor: ['#f6c23e', '#e74a3b', '#858796']
            }]
        }
    });
});
