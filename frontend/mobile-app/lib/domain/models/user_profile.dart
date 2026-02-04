class UserProfile {
  final String user_id;
  final String nickname;
  final String email;
  final bool is_premium;

  const UserProfile({
    required this.user_id,
    required this.nickname,
    required this.email,
    required this.is_premium,
  });
}
