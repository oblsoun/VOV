function popOpen() {
    var modalWrap = document.querySelector('.modal-wrap');
    var modal = document.querySelector('.modal');
    modalWrap.style.display = 'block';
    modal.classList.remove('modal');
}
function popClose() {
    var modalWrap = document.querySelector('.modal-wrap');
    var modalNone = document.querySelector('.modal');
    modalWrap.style.display = 'none';
    modalNone.classList.add('modal');
}