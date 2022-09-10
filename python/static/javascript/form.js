function sendForm(destination, formContent) {
	let httpForm = new XMLHttpRequest();
	httpForm.open("POST", destination, true);
	httpForm.send(formContent);
	httpForm.onload = () => {
		location.reload(true);
	}
}
