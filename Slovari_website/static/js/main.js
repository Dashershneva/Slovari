function validateForm() {
    var x = document.forms["search-form"]["search-item"].value;
	var element = document.querySelector('.search-item-value');
	element.innerHTML = "Результаты поиска: " + x;
	return false;
}
