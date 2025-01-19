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
function setActiveSidebar(new_id){
    var actual_active_item = document.getElementsByClassName("active")[0]
    var new_active_item = document.getElementById(new_id)
    actual_active_item.setAttribute('class', '')
    new_active_item.setAttribute('class', 'active')
}
