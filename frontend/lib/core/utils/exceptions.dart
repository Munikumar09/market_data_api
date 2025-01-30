class EmailNotVerifiedException implements Exception {
  final String message;

  EmailNotVerifiedException(this.message);
}
