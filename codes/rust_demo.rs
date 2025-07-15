// 1. 属性宏（attribute）
#![allow(unused)]
#![feature(associated_type_bounds)] // 特性标志

// 2. 异步函数（async_function）
use async_trait::async_trait;
use reqwest::Client; // 根据[betterprogramming.pub]
use serde_json::json;

// 3. 生命周期注解（lifetime）
struct UserRef<'a> {
    name: &'a str,   // 引用类型字段
    email: &'a str,
}

// 4. 模式匹配（match_arm）
fn parse_status(code: u16) -> &'static str {
    match code {
        200..=299 => "Success",
        404 => "Not Found",
        _ => "Unknown"
    }
}

// 5. 泛型结构体（generic_type）
#[derive(Clone)] // 派生宏
pub struct Pagination<T> {
    data: Vec<T>,
    page: u32,
}

// 6. 特征约束（where_clause）
impl<T: Clone + Send> Pagination<T> {
    pub fn first(&self) -> T where T: Default {
        self.data.first().cloned().unwrap_or_default()
    }
}

// 7. 错误处理宏（macro_invocation）
#[derive(thiserror::Error, Debug)]
pub enum AppError {
    #[error("User not found: {0}")]
    NotFound(#[from] std::io::Error),
    #[error("Invalid data: {0}")]
    InvalidData(String),
}

// 8. 测试模块（test_function）
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_user_creation() {
        let user = User::new(1, "Alice".into());
        assert_eq!(user.name, "Alice");
    }
}

// 9. 文档注释（doc_comment）
/// 用户管理系统
/// 
/// # Examples
/// ```
/// let repo = MemoryRepository::new();
/// repo.save(User::new(1, "Alice"));
/// ```
pub struct UserSystem;

// 10. 闭包（closure_expression）
fn process_users(users: &[User]) {
    users.iter()
        .filter(|u| u.email.is_some())
        .for_each(|u| println!("{}", u.name));
}

// 11. 智能指针（reference_expression）
use std::rc::Rc;
use std::sync::Arc;

fn share_user(user: User) -> Rc<User> {
    Rc::new(user)
}

// 12. 迭代器方法（method_call）
fn collect_ids(users: &[User]) -> Vec<UserId> {
    users.iter()
        .map(|u| u.id)
        .filter(|&id| id > 0)
        .collect()
}

// 13. 特征实现（impl_trait）
impl From<String> for User {
    fn from(name: String) -> Self {
        Self { id: 0, name, email: None }
    }
}

// 14. 异步特征（根据[blog.logrocket.com]）
#[async_trait]
pub trait AsyncRepository: Send + Sync {
    async fn fetch(&self, id: UserId) -> Result<User, AppError>;
}

// 15. 泛型实现（generic_impl）
impl<T> UserRepository for Pagination<T> {
    fn find_by_id(&self, _id: UserId) -> Result<User, UserError> {
        Err(UserError::NotFound)
    }
    
    fn save(&mut self, _user: User) -> Result<(), UserError> {
        Ok(())
    }
}

// 16. 关联类型（associated_type）
pub trait Storage {
    type Error;
    fn store(&self, user: &User) -> Result<(), Self::Error>;
}

// 17. unsafe块（unsafe_block）
fn dangerous_operation() {
    let mut num = 5;
    let r = &num as *const i32;
    
    unsafe {
        println!("Value at {:p}: {}", r, *r);
    }
}

// 18. 条件编译（cfg_attr）
#[cfg_attr(target_os = "linux", path = "linux.rs")]
mod platform;

// 19. 内联汇编（assembly）
#[cfg(target_arch = "x86_64")]
fn get_register() -> u64 {
    let out: u64;
    unsafe {
        std::arch::asm!("mov {}, cr3", out(reg) out);
    }
    out
}

// 20. 过程宏（根据[medium.com]示例）
use axum::Json;

async fn create_user(Json(user): Json<User>) -> Result<Json<User>, AppError> {
    Ok(Json(user))
}

