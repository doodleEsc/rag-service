<?php
// 0. 声明严格类型（type_declaration）
declare(strict_types=1);

// 1. 命名空间定义（namespace_definition）
namespace App\\Models;

// 2. 使用声明分组（group_use_declaration）
use App\\{
    Contracts\\Repository,
    Events\\UserEvent
};

// 3. 文件包含（include_expression）
require_once 'vendor/autoload.php';
include 'config/database.php';

// 4. 接口定义（interface_declaration）
interface UserRepositoryInterface {
    public function findById(int $id): ?User;
    public function save(User $user): bool;
}

// 5. Trait定义（trait_declaration）
trait TimestampsTrait {
    protected $created_at;  // property_declaration
    protected $updated_at;
    
    public function updateTimestamps(): void {
        $this->updated_at = date('Y-m-d H:i:s');  // function_call_expression
    }
}

// 6. 类定义（class_declaration）
#[ORM\Entity]  // attribute (PHP8)
final class User implements UserRepositoryInterface {
    use TimestampsTrait;

    const STATUS_ACTIVE = 1;  // class_const_declaration
    public static int $count = 0;  // static_variable_declaration
    
    public function __construct(
        private int $id,          // promoted_property (PHP8)
        private string $name,
        private ?string $email
    ) {
        $this->created_at = date('Y-m-d H:i:s');
        self::$count++;
    }

    // 7. 析构方法（__destruct）
    public function __destruct() {
        self::$count--;
    }

    // 8. 生成器方法（yield_expression）
    public function getPosts(): Generator {
        foreach ($this->posts as $post) {
            yield $post->title;
        }
    }

    // 9. 匿名类（anonymous_class_creation_expression）
    public function createLogger(): object {
        return new class extends Logger {
            public function log(string $message): void {
                file_put_contents('app.log', $message);
            }
        };
    }
}

// 10. 枚举定义（enum_declaration，PHP8.1）
enum UserStatus: int {
    case Active = 1;      // enum_case_declaration
    case Inactive = 0;
}

// 11. 匹配表达式（match_expression，PHP8.0）
function getStatusText(UserStatus $status): string {
    return match($status) {
        UserStatus::Active => 'Active',
        UserStatus::Inactive => 'Inactive'
    };
}

// 12. 箭头函数（arrow_function，PHP7.4）
$multiplier = fn($x) => $x * 2;

// 13. 空安全操作符（nullsafe_member_call_expression，PHP8.0）
$country = $user?->getAddress()?->country;

// 14. 联合类型（union_type，PHP8.0）
function process(int|string $input): mixed {
    // 15. switch语句（switch_statement）
    switch (true) {
        case is_int($input):
            return $input * 2;
        default:
            return strtoupper($input);
    }
}

// 16. try-catch-finally（try_statement）
try {
    new PDO('mysql:host=localhost');
} catch (PDOException $e) {
    error_log($e);
} finally {
    echo 'Cleanup';
}

// 17. 属性语法（attribute，PHP8）
<<<
User
    @@Deprecated("Use newUser instead", 1.2)
>>>  // heredoc_string
class LegacyUser {}

// 18. 可变参数（variadic_parameter）
function merge(...$arrays): array {
    return array_merge(...$arrays);
}

// 19. 类型别名（type_alias）
class_alias('App\\Models\\User', 'User');

// 20. 嵌套HTML（text_interpolation）
?>
<h1>User List</h1>
<?php foreach ($users as $user): ?>
    <p><?= htmlspecialchars($user->name) ?></p>
<?php endforeach; ?>
