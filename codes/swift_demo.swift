// 新增：条件编译和可用性检查
#if canImport(SwiftUI)
import SwiftUI
#else
import UIKit
#endif

// 导入语句 (已存在)
import Foundation

// 新增：类型别名 (Typealias)
typealias UserID = Int

// 协议定义 (已存在，并扩展)
protocol UserRepositoryProtocol {
    // 新增：关联类型 (Associated Type)
    associatedtype StorageType
    
    func findUser(by id: UserID) -> User?
    func saveUser(_ user: User) throws -> StorageType
    
    // 新增：协议中的默认实现
    func log(message: String) {
        print("[Protocol Log] \(message)")
    }
}

// 结构体定义 (已存在，并扩展)
struct User: Codable, Identifiable { // 新增：遵循多个协议
    // (已存在)
    let id: UserID
    var name: String
    var email: String?
    
    // 新增：嵌套类型 (Nested Type)
    enum Role {
        case admin, member, guest
    }
    var role: Role = .guest
    
    // 新增：静态属性和懒加载属性
    static let defaultDomain = "example.com"
    lazy var profileURL: URL? = {
        return URL(string: "https://\(User.defaultDomain)/profile/\(id)")
    }()
    
    // 新增：属性观察器 (Property Observers)
    var lastLogin: Date? {
        didSet {
            print("User \(name) last login updated to \(lastLogin ?? Date())")
        }
        willSet {
            if let newDate = newValue {
                print("About to set last login to \(newDate)...")
            }
        }
    }
    
    // 计算属性 (已存在)
    var displayName: String {
        return name.isEmpty ? "Unknown" : name
    }
}

// 枚举定义 (已存在，并扩展)
enum UserError: Error {
    // (已存在)
    case notFound
    case invalidData(reason: String) // 新增：带关联值的 case
    case networkError
    
    // 新增：原始值和计算属性
    var localizedDescription: String {
        switch self {
        case .notFound:
            return "The requested user was not found."
        case .invalidData(let reason):
            return "Invalid data provided: \(reason)"
        case .networkError:
            return "A network error occurred."
        }
    }
}

// 新增：泛型函数
func areEqual<T: Equatable>(_ a: T, _ b: T) -> Bool {
    return a == b
}

// 新增：属性包装器 (Property Wrapper)
@propertyWrapper
struct Logged<Value> {
    private var value: Value
    private let name: String

    init(wrappedValue: Value, name: String) {
        self.value = wrappedValue
        self.name = name
    }

    var wrappedValue: Value {
        get { value }
        set {
            print("Property '\(name)' changed to '\(newValue)'")
            value = newValue
        }
    }
}

// 类定义 (已存在，并扩展)
final class UserService: UserRepositoryProtocol { // 新增：final 关键字
    // 新增：实现关联类型
    typealias StorageType = Bool
    
    // 新增：使用属性包装器
    @Logged(name: "user_list")
    private var users: [User] = []
    
    // 新增：弱引用 (weak)
    weak var delegate: AnyObject?
    
    // 初始化方法 (已存在)
    init() {
        self.users = []
    }
    
    // 新增：便利初始化器 (Convenience Initializer)
    convenience init(defaultUsers: [User]) {
        self.init()
        self.users = defaultUsers
    }

    // 新增：析构器 (Deinitializer)
    deinit {
        print("UserService is being deinitialized.")
    }
    
    // 方法实现 (已存在，并扩展)
    func findUser(by id: UserID) -> User? {
        // 新增：guard let else 控制流
        guard !users.isEmpty else {
            print("User database is empty.")
            return nil
        }
        return users.first { $0.id == id }
    }
    
    func saveUser(_ user: User) throws -> StorageType {
        if user.name.isEmpty {
            throw UserError.invalidData(reason: "Name cannot be empty")
        }
        users.append(user)
        log(message: "User saved") // 调用协议的默认实现
        return true
    }
    
    // 新增：inout 参数和可变参数
    func updateUser(id: UserID, with block: (inout User) -> Void) {
        if let index = users.firstIndex(where: { $0.id == id }) {
            block(&users[index])
        }
    }
    
    func addTags(_ tags: String..., to userId: UserID) {
        print("Adding tags \(tags) to user \(userId)")
    }
}

// 新增：Actor 定义 (并发编程)
actor UserAvatarCache {
    private var cache: [UserID: Data] = [:]
    
    func avatar(for userId: UserID) async throws -> Data {
        if let cached = cache[userId] {
            return cached
        }
        // 模拟网络请求
        let url = URL(string: "https://example.com/avatars/\(userId).png")!
        let (data, _) = try await URLSession.shared.data(from: url)
        cache[userId] = data
        return data
    }
}

// 扩展定义 (已存在，并扩展)
extension User {
    // (已存在)
    init(id: UserID, name: String) {
        self.id = id
        self.name = name
        self.email = nil
        self.lastLogin = nil
    }
    
    // 新增：静态方法
    @discardableResult // 新增：@discardableResult 属性
    static func printDefaultDomain() -> String {
        print("Default domain is: \(self.defaultDomain)")
        return self.defaultDomain
    }
}

// 新增：自定义操作符
infix operator <->: AdditionPrecedence
func <->(left: inout User, right: inout User) {
    let tempName = left.name
    left.name = right.name
    right.name = tempName
}

// 新增：@main 结构体作为程序入口
@main
struct AppMain {
    static func main() async { // 新增：async main
        print("--- App Starting ---")
        
        // --- 实例和方法调用 ---
        let service = UserService(defaultUsers: [User(id: 1, name: "Alice")])
        var user = createDefaultUser()
        
        // --- 错误处理: do-catch, try?, try! ---
        do {
            _ = try service.saveUser(user)
        } catch let error as UserError {
            print("Caught expected error: \(error.localizedDescription)")
        } catch {
            print("An unexpected error occurred: \(error)")
        }
        
        let invalidUser = User(id: 2, name: "")
        let saveResult = try? service.saveUser(invalidUser)
        print("Save result for invalid user (try?): \(saveResult ?? false)")

        // --- 控制流 ---
        if let foundUser = service.findUser(by: 1) { // if let
            print("Found user: \(foundUser.displayName)")
        }
        
        // 新增：switch 语句与模式匹配
        user.role = .admin
        switch user.role {
        case .admin:
            print("User is an administrator.")
        case .member, .guest:
            print("User has standard privileges.")
        @unknown default: // 新增：@unknown default
            fatalError("Unhandled role")
        }
        
        // 新增：for-in 循环和范围操作符
        for i in 1...3 {
            print("Loop iteration \(i)")
        }
        
        // 新增：高阶函数 (map, filter) 和闭包
        let userNames = service.users.map { $0.name }
        let guests = service.users.filter { $0.role == .guest }
        
        // --- 并发 ---
        let cache = UserAvatarCache()
        if let avatarData = try? await cache.avatar(for: 1) {
            print("Fetched avatar data, size: \(avatarData.count) bytes.")
        }
        
        // --- 其他 ---
        // 新增：使用自定义操作符
        var userA = User(id: 10, name: "A")
        var userB = User(id: 11, name: "B")
        userA <-> userB
        print("Swapped names: A is now \(userA.name), B is now \(userB.name)")
        
        // 新增：类型检查和转换
        let someObject: Any = "Hello, Swift"
        if someObject is String {
            if let stringValue = someObject as? String {
                print("Object is a string: \(stringValue)")
            }
        }
        
        // 新增：defer 语句
        defer {
            print("--- App Finishing ---")
        }
        
        // 新增：使用 Magic Literals
        print("Executed from file: \(#file) at line: \(#line)")
    }
}

// 函数定义 (已存在)
func createDefaultUser() -> User {
    return User(id: 0, name: "Default User")
}

