<!DOCTYPE html>
<html>
<head>
	<meta http-equiv = "content-type" content = "text/html; charset = utf-8"/>
	<meta name="author" content="梁钧凯"/>
	<title>分析结果</title>
	<script src="https://cdn.bootcss.com/particles.js/2.0.0/particles.js"></script>
	<link rel="stylesheet" media="all" href="css/result-style.css"/>
</head>
<body>
	<div id="particles-js"></div>
	<script src="scripts/particles-result.js"></script>
	<div id="total">
	<h1>分析结果</h1>
	<?php
	$mid=$_GET['mid'];
	$num=$_GET['num'];
	
	$json=shell_exec("python3 scripts/weibo.py $mid $num");
	$weibo=json_decode($json,true);
	$num=count($weibo)-2;//0 username 1 this_text
	
	if($num<0)
		{
		echo "<div id=\"head\" class=\"part\">查询微博不存在！<br>查询微博mid：$mid<br><button id=\"button\" type=\"button\" onclick=\"location.href='index.html'\">返回</button></div><br>";
		exit;
		}

	$pattern="/#([^#]*)#/";
	
	echo "<div id=\"head\" class=\"part\">微博用户：$weibo[0]<br>查询微博mid：$mid<br>参考最新微博数量：$num<br><button id=\"button\" type=\"button\" onclick=\"location.href='index.html'\">返回</button></div><br>";
	
	$label_meaning=["乐","好","哀","恶","怒","惧","惊"];
	$len=7;
	
	for($i=0;$i<=$num;++$i)
		{
		$record["id$i"]["text"]=$weibo[$i+1];
		if(preg_match_all($pattern,$weibo[$i+1],$matches))
			$record["id$i"]["subject"]=$matches[1];
		else
			$record["id$i"]["subject"]=["无"];
		}
		
	$para=str_replace("\"","\\\"",json_encode($record));
	// echo $para;
	$vec=shell_exec("python3 scripts/ECNN.py $num \"$para\"");
	$output=json_decode($vec,true);
	// var_dump($output);
	
	$sum_s=0;
	$sum_v=[0,0,0,0,0,0,0];
	for($i=0;$i<=$num;++$i)
		{
		$record["id$i"]["result"]=[];
		$sim=floatval($output[$i][0]);
		$sum_s+=$sim;
		for($j=0;$j<$len;++$j)
			{
			$output[$i][$j+1]=floatval($output[$i][$j+1]);
			$sum_v[$j]+=$output[$i][$j+1]*$sim;
			if($output[$i][$j+1]>=0.5)
				array_push($record["id$i"]["result"],$label_meaning[$j]);
			}
		}
	
	// echo "$sum_s";
	// var_dump($sum_v);
	$label=[];
	for($i=0;$i<$len;++$i)
		if($sum_v[$i]/$sum_s>=0.5)
			array_push($label,$label_meaning[$i]);
	
	echo "<div id=\"sum\" class=\"part\"><div class=\"title\">综合分析：</div>";
	if(count($label))
		{
		echo "&emsp;&emsp;&emsp;&emsp;";
		foreach($label as $value)
			{
			echo "&emsp;<div class=\"label\">$value</div>";
			}
		}
	else
		echo "&emsp;&emsp;无情感倾向";
	echo "</div><br>";
	
	for($i=0;$i<=$num;++$i)
		{
		echo "<div class=\"part\">";
		if($i==0)
			echo "<div class=\"title\">查询微博文本：</div>";
		else
			echo "<div class=\"title\">最近第 $i 条微博：</div>";
		echo "&emsp;&emsp;".$record["id$i"]["text"]."<br>";
		echo "<div class=\"title\">主题：</div>";
		foreach($record["id$i"]["subject"] as $value)
			echo "&emsp;&emsp;$value<br>";
		
		echo "<div class=\"title\">情感分析：</div>";
		if(count($record["id$i"]["result"]))
			{
			echo "&emsp;&emsp;&emsp;&emsp;";
			foreach($record["id$i"]["result"] as $value)
				{
				echo "&emsp;<div class=\"label\">$value</div>";
				}
			}
		else
			echo "&emsp;&emsp;无情感倾向";
		echo "</div>";
		echo "<br>";
		}
	?>
	</div>
</body>
</html>