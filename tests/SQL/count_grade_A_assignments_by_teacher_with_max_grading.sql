-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
SELECT COUNT(*) AS grade_A
FROM assignments
WHERE teacher_id = (
    SELECT teacher_id
    FROM (
        SELECT teacher_id, COUNT(*) AS graded_count
        FROM assignments
        WHERE grade = 'A'
        GROUP BY teacher_id
        ORDER BY graded_count DESC
        LIMIT 1
    ) AS max_grading_teacher
)
AND grade = 'A';