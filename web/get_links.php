<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: max-age=300'); // 5分钟浏览器缓存

// 启用错误报告用于调试
error_reporting(E_ALL);
ini_set('display_errors', 0); // 生产环境设为0

// 设置更长的超时时间
set_time_limit(30);

// 缓存机制
$cache_file = 'github_releases_cache.json';
$cache_time = 3600; // 1小时缓存

// 如果缓存文件存在且未过期，直接返回缓存数据
if (file_exists($cache_file) && (time() - filemtime($cache_file) < $cache_time)) {
    $cached_data = file_get_contents($cache_file);
    if ($cached_data !== false && $cached_data !== '') {
        echo $cached_data;
        exit;
    }
}

$repo_owner = 'Qxyz17';
$repo_name = '123pan';

// 使用GitHub API
$api_url = "https://api.github.com/repos/{$repo_owner}/{$repo_name}/releases";

// 尝试使用GitHub API
$response = getFromGitHubAPI($api_url);

if ($response === false || $response === '') {
    // 如果GitHub API失败，使用备用数据源
    $response = getFromAlternativeSource();
    
    if ($response === false || $response === '') {
        // 如果所有方法都失败，尝试使用缓存（即使已过期）
        if (file_exists($cache_file)) {
            $cached_data = file_get_contents($cache_file);
            if ($cached_data !== false && $cached_data !== '') {
                echo $cached_data;
                exit;
            }
        }
        
        // 返回静态数据
        echo getStaticReleases();
        exit;
    }
}

// 保存到缓存
if ($response !== false && $response !== '') {
    @file_put_contents($cache_file, $response);
}

// 输出结果
echo $response;
exit;

/**
 * 从GitHub API获取数据
 */
function getFromGitHubAPI($url) {
    // 设置请求头
    $options = [
        'http' => [
            'method' => 'GET',
            'header' => [
                'User-Agent: 123pan-Download-Page/1.0',
                'Accept: application/vnd.github.v3+json',
                'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8'
            ],
            'timeout' => 15,
            'ignore_errors' => true
        ],
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
        ]
    ];
    
    $context = stream_context_create($options);
    
    // 尝试使用file_get_contents
    $response = @file_get_contents($url, false, $context);
    
    if ($response === false || empty($response)) {
        // 尝试使用cURL
        $response = getViaCurl($url);
    }
    
    if ($response === false || empty($response)) {
        return false;
    }
    
    // 验证响应
    $data = json_decode($response, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        return false;
    }
    
    // 检查是否有错误信息
    if (isset($data['message'])) {
        if (strpos($data['message'], 'API rate limit') !== false || 
            strpos($data['message'], 'rate limit') !== false) {
            // GitHub API限制
            error_log('GitHub API rate limit exceeded');
            return false;
        }
        // 其他API错误
        return false;
    }
    
    // 如果没有数据或不是数组
    if (!is_array($data) || empty($data)) {
        return false;
    }
    
    // 处理数据格式
    $processed_releases = [];
    foreach ($data as $release) {
        // 跳过草稿版
        if (isset($release['draft']) && $release['draft'] === true) {
            continue;
        }
        
        // 跳过预发布版（如果需要只显示稳定版）
        // if (isset($release['prerelease']) && $release['prerelease'] === true) {
        //     continue;
        // }
        
        $processed_release = [
            'tag_name' => $release['tag_name'] ?? '',
            'name' => $release['name'] ?? $release['tag_name'],
            'body' => $release['body'] ?? '',
            'published_at' => $release['published_at'] ?? '',
            'assets' => []
        ];
        
        if (isset($release['assets']) && is_array($release['assets'])) {
            foreach ($release['assets'] as $asset) {
                $processed_release['assets'][] = [
                    'name' => $asset['name'] ?? '',
                    'size' => $asset['size'] ?? 0,
                    'browser_download_url' => $asset['browser_download_url'] ?? '',
                    'content_type' => $asset['content_type'] ?? 'application/octet-stream'
                ];
            }
        }
        
        $processed_releases[] = $processed_release;
    }
    
    // 如果没有处理后的发布信息
    if (empty($processed_releases)) {
        return false;
    }
    
    return json_encode($processed_releases, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}

/**
 * 使用cURL获取数据
 */
function getViaCurl($url) {
    if (!function_exists('curl_init')) {
        return false;
    }
    
    $ch = curl_init();
    
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_USERAGENT => '123pan-Download-Page/1.0',
        CURLOPT_HTTPHEADER => [
            'Accept: application/vnd.github.v3+json',
            'Accept-Language: zh-CN,zh;q=0.9'
        ],
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 15,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_FAILONERROR => false,
        CURLOPT_ENCODING => '', // 接受gzip压缩
        CURLOPT_CONNECTTIMEOUT => 10
    ]);
    
    $response = curl_exec($ch);
    
    if (curl_errno($ch)) {
        curl_close($ch);
        return false;
    }
    
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($http_code === 200 && !empty($response)) {
        return $response;
    }
    
    return false;
}

/**
 * 备用数据源 - 返回静态数据
 */
function getFromAlternativeSource() {
    // 尝试获取最新版本的信息
    $latest_url = "https://api.github.com/repos/Qxyz17/123pan/releases/latest";
    $options = [
        'http' => [
            'method' => 'GET',
            'header' => [
                'User-Agent: 123pan-Download-Page/1.0',
                'Accept: application/vnd.github.v3+json'
            ],
            'timeout' => 10
        ]
    ];
    
    $context = stream_context_create($options);
    $response = @file_get_contents($latest_url, false, $context);
    
    if ($response !== false && !empty($response)) {
        $data = json_decode($response, true);
        
        if (json_last_error() === JSON_ERROR_NONE && isset($data['tag_name'])) {
            $processed_release = [
                'tag_name' => $data['tag_name'] ?? '',
                'name' => $data['name'] ?? $data['tag_name'],
                'body' => $data['body'] ?? '最新版本',
                'published_at' => $data['published_at'] ?? date('Y-m-d\TH:i:s\Z'),
                'assets' => []
            ];
            
            if (isset($data['assets']) && is_array($data['assets'])) {
                foreach ($data['assets'] as $asset) {
                    $processed_release['assets'][] = [
                        'name' => $asset['name'] ?? '',
                        'size' => $asset['size'] ?? 0,
                        'browser_download_url' => $asset['browser_download_url'] ?? '',
                        'content_type' => $asset['content_type'] ?? 'application/octet-stream'
                    ];
                }
            }
            
            return json_encode([$processed_release], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        }
    }
    
    // 如果都失败了，返回静态数据
    return getStaticReleases();
}

/**
 * 返回静态发布数据
 */
function getStaticReleases() {
    $static_releases = [
        [
            'tag_name' => 'v1.0.0',
            'name' => '123pan 最新版本',
            'body' => '如果无法自动获取发布信息，请直接访问 GitHub Releases 页面下载最新版本。',
            'published_at' => date('Y-m-d\TH:i:s\Z'),
            'assets' => [
                [
                    'name' => '前往 GitHub Releases 下载',
                    'size' => 0,
                    'browser_download_url' => 'https://github.com/Qxyz17/123pan/releases',
                    'content_type' => 'text/html'
                ],
                [
                    'name' => '直接下载最新版本',
                    'size' => 0,
                    'browser_download_url' => 'https://github.com/Qxyz17/123pan/releases/latest',
                    'content_type' => 'application/octet-stream'
                ]
            ]
        ]
    ];
    
    return json_encode($static_releases, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}
?>
