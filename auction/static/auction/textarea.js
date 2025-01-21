$('textarea').keypress(function(e) {
    if (e.keyCode == 13) {
      e.preventDefault();
      this.value = this.value.substring(0, this.selectionStart) + "" + "\n" + this.value.substring(this.selectionEnd, this.value.length);
    }
});