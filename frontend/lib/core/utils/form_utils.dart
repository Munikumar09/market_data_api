import 'package:flutter/widgets.dart';

class FormUtils {
  static bool validate(GlobalKey<FormState> formKey) {
    if (formKey.currentState?.validate() ?? false) {
      formKey.currentState?.save();
      return true;
    }
    return false;
  }
}
