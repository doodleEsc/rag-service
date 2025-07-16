// 1. 包和导入声明
/*
 *
 */
package com.example.testing

import kotlin.random.Random
import kotlinx.coroutines.*
import java.io.File as JavaFile // 导入别名

// 2. 顶级属性和函数
const val MAX_RETRIES = 3
fun logMessage(message: String) = println("[LOG] $message")

/**
 * 这是 KDoc 注释，用于测试文档解析。
 * @param name 要问候的人名
 */
@Deprecated("Use new greeting function", ReplaceWith("greetNew(name)")) // 注解
fun `function with spaces`(name: String) { // 带反引号的函数名
    println("Hello, $name!")
}

// 3. 接口、枚举类和密封类
interface Serializable {
    fun toJson(): String
    
    // 接口中的默认实现
    fun log() {
        logMessage("Serializing object...")
    }
}

enum class Color(val hex: String) {
    RED("#FF0000"),
    GREEN("#00FF00"),
    BLUE("#00FFFF"); // 分号是可选的

    fun isPrimary(): Boolean {
        return this != BLUE
    }
}

sealed interface Result<out T> { // 密封接口和型变 (out)
    data class Success<T>(val data: T) : Result<T>
    data class Error(val exception: Exception) : Result<Nothing>
    object Loading : Result<Nothing>
}

// 4. 类 (常规、数据、对象、伴生)
open class Person(val name: String) {
    open fun describe() = "Person named $name"
}

data class User(
    val id: Long,
    var username: String,
    val email: String? // 可空类型
) : Person(username), Serializable {

    // 属性 (自定义 getter/setter, lateinit, by lazy)
    var aGe: Int = 0
        set(value) {
            field = if (value < 0) 0 else value
        }

    lateinit var profilePictureUrl: String

    val aUthToken: String by lazy {
        "token-${Random.nextLong()}"
    }

    // init 块
    init {
        require(username.isNotBlank()) { "Username must not be blank" }
    }

    // 次构造函数
    constructor(id: Long, username: String) : this(id, username, null) {
        logMessage("User created with no email.")
    }

    // 方法重写
    override fun describe(): String = "User $username with ID $id"

    // 实现接口方法
    override fun toJson(): String {
        // 原始字符串
        return """
            {
                "id": $id,
                "username": "$username",
                "email": "${email ?: "null"}"
            }
        """.trimIndent()
    }
    
    companion object Factory { // 伴生对象
        fun createGuest(): User {
            return User(0, "Guest")
        }
    }
}

object AppConfig { // 单例对象
    const val API_URL = "https://api.example.com"
}

// 5. 扩展、中缀和操作符函数
fun String.shout() = this.uppercase() + "!!!"

infix fun Int.plusFive(other: Int) = this + 5 + other

operator fun User.inc(): User { // 操作符重载
    return this.copy(id = this.id + 1)
}

// 6. 泛型
fun <T> singletonListOf(item: T): List<T> {
    return listOf(item)
}

class Box<T: Any>(var content: T) // 泛型和约束

// 7. 主函数，演示所有特性
fun main() = runBlocking { // 协程上下文
    logMessage("Starting application from ${AppConfig.API_URL}")

    // 实例创建和方法调用
    var user = User.createGuest()
    user.aGe = -10 // 使用自定义 setter
    println(user.shout()) // 扩展函数
    println(5 plusFive 10) // 中缀函数
    user++ // 操作符重载
    println("User ID after increment: ${user.id}")

    // 空安全
    val emailLength = user.email?.length ?: 0 // elvis 操作符
    println("Email length: $emailLength")
    
    // 强制解包 (不推荐，仅用于测试)
    try {
        val nonNullEmail: String = user.email!!
    } catch (e: NullPointerException) {
        println("Caught expected NPE.")
    }

    // 控制流 - if/else 表达式
    val status = if (user.id == 0L) "Guest" else "Registered"
    println("User status: $status")

    // 控制流 - when 表达式
    val result: Result<User> = Result.Success(user)
    val message = when (result) {
        is Result.Success -> "Success! Data: ${result.data.username}"
        is Result.Error -> "Error: ${result.exception.message}"
        Result.Loading -> "Still loading..."
    }
    println(message)

    // 控制流 - 循环和标签
    outerLoop@for (i in 1..3) {
        for (j in 1..3) {
            if (i * j > 5) {
                println("Breaking outer loop from inner at i=$i, j=$j")
                break@outerLoop
            }
        }
    }
    (1..5).filter { it % 2 == 0 }.forEach { println(it) } // Lambda 和高阶函数

    // 解构声明
    val (id, name, _) = user // 忽略 email
    println("Destructured: ID=$id, Name=$name")
    
    // 作用域函数
    user.apply {
        username = "NewGuest"
    }.let {
        println("User updated to: ${it.toJson()}")
    }
    
    // 协程
    val job = launch {
        delay(100L)
        println("Coroutine launch finished.")
    }
    val deferred = async {
        delay(200L)
        "Async result"
    }
    println(deferred.await())
    job.join()
    
    // 类型检查
    val person: Person = user
    if (person is User) {
        println("Type check success: person is a User. Auth token: ${person.aUthToken}") // 智能转换
    }
    
    println("Application finished.")
}

