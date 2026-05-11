// Utilidad compartida para validar la fortaleza de las contrasenas en Flutter.
class PasswordRules {
  static final RegExp _pattern = RegExp(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&\.\-\_#]).{8,}$',
  );

  static const String helpText =
      'Minimo 8 caracteres, con mayuscula, minuscula, numero y simbolo.';

  static bool isStrong(String value) {
    return _pattern.hasMatch(value);
  }

  static String? validateRequired(String? value) {
    final text = value ?? '';
    if (text.isEmpty) {
      return 'Campo requerido';
    }
    if (!isStrong(text)) {
      return helpText;
    }
    return null;
  }
}
