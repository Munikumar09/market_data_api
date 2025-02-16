import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:frontend/core/constants/storage_keys.dart';
import 'package:frontend/core/utils/exceptions/auth_exceptions.dart';

/// Defines methods for secure token storage and management.
abstract class TokenStorage {
  /// Saves access and refresh tokens.
  Future<void> saveTokens(
      {required String accessToken, required String refreshToken});

  /// Retrieves saved tokens.
  Future<({String? accessToken, String? refreshToken})> getTokens();

  /// Clears saved tokens.
  Future<void> clearTokens();

  /// Parses authentication tokens from the provided data.
  ({String accessToken, String refreshToken}) parseAuthTokens(
      Map<String, dynamic> data);
}

/// A service that securely stores tokens using FlutterSecureStorage.
class SecureStorageService implements TokenStorage {
  final FlutterSecureStorage _secureStorage;
  SecureStorageService({FlutterSecureStorage? secureStorage})
      : _secureStorage = secureStorage ?? const FlutterSecureStorage();

  /// Saves access and refresh tokens into secure storage.
  @override
  Future<void> saveTokens(
      {required String accessToken, required String refreshToken}) async {
    try {
      // Write tokens concurrently.
      await Future.wait([
        _secureStorage.write(key: StorageKeys.accessToken, value: accessToken),
        _secureStorage.write(
            key: StorageKeys.refreshToken, value: refreshToken),
      ]);
    } on PlatformException catch (e) {
      throw TokenStorageException('Failed to save tokens: ${e.message}');
    }
  }

  /// Retrieves tokens from secure storage.
  @override
  Future<({String? accessToken, String? refreshToken})> getTokens() async {
    try {
      // Read tokens concurrently.
      final results = await Future.wait([
        _secureStorage.read(key: StorageKeys.accessToken),
        _secureStorage.read(key: StorageKeys.refreshToken),
      ]);
      return (accessToken: results[0], refreshToken: results[1]);
    } on PlatformException catch (e) {
      throw TokenStorageException('Failed to read tokens: ${e.message}');
    }
  }

  /// Clears tokens from secure storage.
  @override
  Future<void> clearTokens() async {
    try {
      // Delete tokens concurrently.
      await Future.wait([
        _secureStorage.delete(key: StorageKeys.accessToken),
        _secureStorage.delete(key: StorageKeys.refreshToken),
      ]);
    } on PlatformException catch (e) {
      throw TokenStorageException('Failed to clear tokens: ${e.message}');
    }
  }

  /// Parses and validates the authentication tokens from a response.
  @override
  ({String accessToken, String refreshToken}) parseAuthTokens(
      Map<String, dynamic> data) {
    final accessToken = data[StorageKeys.accessToken] as String?;
    final refreshToken = data[StorageKeys.refreshToken] as String?;

    if (accessToken == null || refreshToken == null) {
      throw const FormatException('Invalid token format in response');
    }

    return (accessToken: accessToken, refreshToken: refreshToken);
  }
}
