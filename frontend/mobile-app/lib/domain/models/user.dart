class User {
  final int id; // ID는 보통 int로 옴 (필요시 String으로 변경)
  final String name;
  final String email;

  User({
    required this.id,
    required this.name,
    required this.email,
  });

  // 백엔드 JSON -> Dart 객체 변환 (Factory Constructor)
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      // DB 스키마에 따르면 user_id임
      id: json['user_id'] ?? json['id'] ?? 0,
      name: json['nickname'] ?? '',
      email: json['email'] ?? '',
    );
  }
}