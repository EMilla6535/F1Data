function toggleSidebar(){
    var sidebar = document.getElementById('sidebar');
    var showButton = document.getElementById('show-button');
    var mainContent = document.getElementById('main-content');
    if (sidebar.style.display === 'none'){
        sidebar.style.display = 'flex';
        showButton.style.display = 'none';
        //mainContent.style.marginLeft = '200px';
    } else {
        sidebar.style.display = 'none';
        showButton.style.display = 'block';
        //mainContent.style.marginLeft = '0';
    }
}
