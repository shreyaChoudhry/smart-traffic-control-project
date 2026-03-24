// CLOCK

setInterval(()=>{

let d = new Date()

document.getElementById("time").innerHTML = d.toLocaleTimeString()

},1000)


// CHART

const ctx = document.getElementById('trafficChart')

const trafficChart = new Chart(ctx,{

type:'bar',

data:{

labels:['Lane1','Lane2','Lane3','Lane4'],

datasets:[{

label:'Vehicles',

data:[0,0,0,0],

backgroundColor:'#38bdf8'

}]

}

})


// REALTIME DATA

function updateData(){

fetch("/data")

.then(res=>res.json())

.then(data=>{

document.getElementById("vehicles").innerText = data.vehicles
document.getElementById("density").innerText = data.density
document.getElementById("priority").innerText = data.priority

document.getElementById("lane1").innerText = data.lane1
document.getElementById("lane2").innerText = data.lane2
document.getElementById("lane3").innerText = data.lane3
document.getElementById("lane4").innerText = data.lane4

document.getElementById("timer").innerText = data.timer


trafficChart.data.datasets[0].data = [
data.lane1,
data.lane2,
data.lane3,
data.lane4
]

trafficChart.update()


const lights = document.querySelectorAll(".light")

lights.forEach(light=>{

light.classList.remove("green")
light.classList.add("red")

})

lights[data.priority-1].classList.remove("red")
lights[data.priority-1].classList.add("green")

})

}

setInterval(updateData,1000)
