document.addEventListener('DOMContentLoaded', () => {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        console.log("connected!");
        
        document.getElementById('login').onclick = () => {
            const name = document.getElementById('name').value;
            localStorage.setItem('name', name);
        };
        
        socket.emit('joined');

        
        document.getElementById('send').onclick = () => {
            const txt = document.getElementById('text').value;
            document.getElementById('text').value ='';
            socket.emit('send', {'txt': txt});
        };

        document.getElementById('leave_room').onclick = () => {

            socket.emit('leave');
        };

    });
        
   socket.on('announce join', data => {
    const p = `${data.username}`;
    document.getElementById('add_item').value += '<'+p+ ' has joined the room!'+'>'+'\n';
   });

   socket.on('left', data => {
    const p = `${data.username}`;
    document.getElementById('add_item').value += '<'+p+ ' has left the room!'+'>'+'\n';
   });

    socket.on('recieve', data => {
        const t = `${data.time_stamp}`;
        const p = `${data.username}`;
        const li = `${data.txt}`;
        document.getElementById('add_item').value +='['+t+']' + '<'+p+'>'+ '' +li+ '\n';
    });
});