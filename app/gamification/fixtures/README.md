Users data:
| id | Andrew ID | Password | First Name | Last Name | Email | is_staff |
| -- | --------- | -------- | ---------- | --------- | ----- | -------- |
|  1 | admin1    | admin1-password | One | Admin     | admin1@example.com | true  |
|  2 | admin2    | admin2-password | Two | Admin     | admin2@example.com | true  |
|  3 | user1     | user1-password | One  | User      | user1@example.com  | false |
|  4 | user2     | user2-password | Two  | User      | user2@example.com  | false |
|  5 | user3     | user3-password | Three | User     | user3@example.com  | false |
|  6 | user4     | user4-password | Four | User      | user4@example.com  | false |

Courses data:
| id | Number | Name | Syllabus | Semester | Visible |
| -- | ------ | ---- | -------- | -------- | ------- |
| 1  | 18652  | Foundations of Software Engineering   | In this course ...       | Fall 2021   | true  |
| 2  | 18668  | Data Science for Software Engineering | Building, operating ...  | Spring 2022 | true  |
| 3  | 18661  | Introduction to Machine Learning for Engineers | This course ... | Spring 2024 | false |
| 4  | 18749  | Building Reliable Distributed Systems | The course provides ...  | Summer 2024 | false |
| 5  | 18664  | Software Refactoring                  | Refactoring aims to ...  | Spring 2022 | true  |

<!-- Course registration:
| id | Role | Course ID | Course Number | User ID | User Andrew ID |
| -- | ---- | --------- | ------------- | ------- | -------------- |
| 1  | Instructor | 1   | 18652         | 1       | admin1         |
| 2  | Instructor | 2   | 18668         | 2       | admin2         |
| 3  | Instructor | 3   | 18661         | 2       | admin2         |
| 4  | Instructor | 4   | 18749         | 1       | admin1         |
| 5  | Instructor | 5   | 18664         | 1       | admin1         |
| 6  | Instructor | 5   | 18664         | 2       | admin2         |
| 7  | Student    | 1   | 18652         | 3       | user1          |
| 8  | Student    | 1   | 18652         | 4       | user2          |
| 9  | Student    | 1   | 18652         | 5       | user3          |
| 10 | TA         | 1   | 18652         | 6       | user4          | -->

Assignments data:
| id | Name | Course ID | Course Number | Description | Type | Submission Type | Total Score | Weight |
| -- | ---- | --------- | ------------- | ----------- | ---- | --------------- | ----------- | ------ |
| 1 | Chat Room Iteration 1 | 1 | 18652 | Implement a simple ... | Team       | URL  | 100 | 0.25 |
| 2 | Chat Room Iteration 2 | 1 | 18652 | Implement a simple ... | Team       | URL  | 100 | 0.4  |
| 3 | Final Exam            | 1 | 18652 | The total point of ... | Individual | Text | 70  | 0.35 |

Entities data:
| id | Course ID | Course Number | Type | Name | Members Andrew ID |
| -- | --------- | ------------- | ---- | ---- | ----------------- |
| 2  | 1 | 18652 | Team | T1   | user1, user2|
| 3  | 1 | 18652 | Team | T2   | user3 |

Summarized Course data:
| Course ID | Course Number | Instructors | TAs | Students | Assignments ID | Entities ID |
| --------- | ------------- | ----------- | --- | -------- | -------------- | ----------- |
| 1 | 18652 | admin1 | user4 | user1, user2, user3 | 1, 2, 3 | 2, 3|
| 2 | 18668 | admin2 | /     | / | / | / |
| 3 | 18661 | admin2 | /     | / | / | / |
| 4 | 18749 | admin1 | /     | / | / | / |
| 5 | 18664 | admin1, admin2 | / | / | / | / |
