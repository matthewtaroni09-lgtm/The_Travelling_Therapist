// let currentYear = document.getElementById('current-year');
// currentYear.innerText = new Date().getFullYear();
// alert('hello');

// Demographics Chart
// const demographicsLabels = [
//     'Under 18',
//     '18 - 65',
//     'Over 65',
// ];

// const data = {
//     labels: demographicsLabels,
//     datasets: [{
//         label: 'Client Demographics',
//         backgroundColor: [
//             'rgb(255, 99, 132)',
//             'rgb(54, 162, 235)',
//             'rgb(255, 205, 86)'
//         ],
//         borderColor: [
//             'rgb(255, 99, 132)',
//             'rgb(54, 162, 235)',
//             'rgb(255, 205, 86)'
//         ],
//         data: [20, 25, 55],
//     }]
// };

// const config = {
//     type: 'doughnut',
//     data: data,
//     options: {
//         responsive: true,
//         layout: {
//             padding: 20
//         },
//         plugins: {
//             title: {
//                 display: true,
//                 text: 'Client Demographics',
//                 font: {
//                     size: 16
//                 },
//                 color: '#000',
//                 padding: {
//                     bottom: 30
//                 }
//             },
//             legend: {
//                 display: true,
//                 position: 'bottom',
//             }
//         }
//     }
// };

// const demographics = new Chart(
//     document.getElementById('demographics'),
//     config
// );


// // Area of Practice Chart
// const areasOfPracticeLabels = [
//     'MSK',
//     'Neuro',
//     'CardioResp',
// ];

// const areasOfPracticeData = {
//     labels: areasOfPracticeLabels,
//     datasets: [{
//         label: 'Area of Practice',
//         backgroundColor: [
//             'rgb(255, 99, 132)',
//             'rgb(54, 162, 235)',
//             'rgb(255, 205, 86)'
//         ],
//         borderColor: [
//             'rgb(255, 99, 132)',
//             'rgb(54, 162, 235)',
//             'rgb(255, 205, 86)'
//         ],
//         data: [50, 300, 10],
//     }]
// };

// const areasOfPracticeConfig = {
//     type: 'doughnut',
//     data: areasOfPracticeData,
//     options: {
//         responsive: true,
//         layout: {
//             padding: 20
//         },
//         plugins: {
//             title: {
//                 display: true,
//                 text: 'Area of Practice',
//                 font: {
//                     size: 16
//                 },
//                 color: '#000',
//                 padding: {
//                     bottom: 30
//                 }
//             },
//             legend: {
//                 display: true,
//                 position: 'bottom'
//             }
//         }
//     }
// };

// const areasOfPracticeChart = new Chart(
//     document.getElementById('areaOfPractice'),
//     areasOfPracticeConfig
// );