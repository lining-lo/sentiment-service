"""固定四表检索 SQL"""

from sqlalchemy import text


def db_sql_statement():
    """构建固定四表的关键词检索 SQL"""
    return text("""
        SELECT * FROM (
            SELECT 'douyin' AS platform, 'douyin_aweme' AS source_table, id AS mysql_primary_key, title AS title_or_content, create_time AS published_at,
                    liked_count AS eng_likes, comment_count AS eng_comments, share_count AS eng_shares, collected_count AS eng_collects, 0 AS eng_replies,
                liked_count + comment_count * 3 + share_count * 4 + collected_count * 2 AS hotness_score
            FROM douyin_aweme WHERE title LIKE :search_term
            UNION ALL
            SELECT 'douyin' AS platform, 'douyin_aweme_comment' AS source_table, id AS mysql_primary_key, content AS title_or_content, create_time AS published_at,
                like_count AS eng_likes, 0 AS eng_comments, 0 AS eng_shares, 0 AS eng_collects, sub_comment_count AS eng_replies,
                like_count + sub_comment_count * 3 AS hotness_score
            FROM douyin_aweme_comment WHERE content LIKE :search_term
            UNION ALL
            SELECT 'weibo' AS platform, 'weibo_note' AS source_table, id AS mysql_primary_key, content AS title_or_content, create_time AS published_at,
                liked_count AS eng_likes, comments_count AS eng_comments, shared_count AS eng_shares, 0 AS eng_collects, 0 AS eng_replies,
                liked_count + comments_count * 4 + shared_count * 5 AS hotness_score
            FROM weibo_note WHERE content LIKE :search_term
            UNION ALL
            SELECT 'weibo' AS platform, 'weibo_note_comment' AS source_table, id AS mysql_primary_key, content AS title_or_content, create_time AS published_at,
                comment_like_count AS eng_likes, 0 AS eng_comments, 0 AS eng_shares, 0 AS eng_collects, sub_comment_count AS eng_replies,
                comment_like_count + sub_comment_count * 3 AS hotness_score
            FROM weibo_note_comment WHERE content LIKE :search_term
        ) AS db_call_candidates
        ORDER BY hotness_score DESC, published_at DESC
        LIMIT :limit
    """)


def vector_sql_statement():
    """构建固定四表的向量同步 SQL"""
    return text("""
        SELECT 'douyin' AS platform, 'douyin_aweme' AS source_table, id AS mysql_primary_key, title AS content, create_time AS published_at,
            liked_count AS eng_likes, comment_count AS eng_comments, share_count AS eng_shares, collected_count AS eng_collects, 0 AS eng_replies,
            liked_count + comment_count * 4 + share_count * 5 + collected_count * 2 AS hotness_score
        FROM douyin_aweme
        UNION ALL
        SELECT 'douyin' AS platform, 'douyin_aweme_comment' AS source_table, id AS mysql_primary_key, content AS content, create_time AS published_at,
            like_count AS eng_likes, 0 AS eng_comments, 0 AS eng_shares, 0 AS eng_collects, sub_comment_count AS eng_replies,
            like_count + sub_comment_count * 3 AS hotness_score
        FROM douyin_aweme_comment
        UNION ALL
        SELECT 'weibo' AS platform, 'weibo_note' AS source_table, id AS mysql_primary_key, content AS content, create_time AS published_at,
            liked_count AS eng_likes, comments_count AS eng_comments, shared_count AS eng_shares, 0 AS eng_collects, 0 AS eng_replies,
            liked_count + comments_count * 4 + shared_count * 5 AS hotness_score
        FROM weibo_note
        UNION ALL
        SELECT 'weibo' AS platform, 'weibo_note_comment' AS source_table, id AS mysql_primary_key, content AS content, create_time AS published_at,
            comment_like_count AS eng_likes, 0 AS eng_comments, 0 AS eng_shares, 0 AS eng_collects, sub_comment_count AS eng_replies,
            comment_like_count + sub_comment_count * 3 AS hotness_score
        FROM weibo_note_comment
    """)