function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("👤工具表")
    .addItem("创建筛选表", "createFilterTable")
    .addItem("删除筛选表", "deleteFilterTable")
    .addSeparator()
    .addItem("创建搜索表", "createSearchTable")
    .addItem("删除搜索表", "deleteSearchTable")
    .addToUi();
}

function setAllRangeStyle(sheet) {
  //获取筛选表的所有单元格
  const allRange = sheet.getRange(1, 1, sheet.getMaxRows(), sheet.getMaxColumns());
  //设置格式
  allRange.setVerticalAlignment("middle");
  allRange.setHorizontalAlignment("center");
  allRange.setFontFamily("Roboto");
  allRange.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);
  //获取表头，设置粗体
  const header = sheet.getRange("A1:1");
  header.setFontWeight("bold");
}

function createFilterTable() {
  //创建新的筛选表之前先删掉旧的，如果有的话
  deleteFilterTable();

  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  //当前活跃的表格
  const sheet = spreadsheet.getActiveSheet();

  let sheetName = sheet.getName();
  let newHelperSheetName = `[${sheetName}]辅助`;
  let newFilterSheetName = `[${sheetName}]筛选`;

  //插入两个新表
  const newHelperSheet = spreadsheet.insertSheet();
  newHelperSheet.setName(newHelperSheetName);
  const newFilterSheet = spreadsheet.insertSheet();
  newFilterSheet.setName(newFilterSheetName);

  //定义特殊值
  const allVal = "[[全部]]";
  const nullVal = "[[空]]";
  const notNullVal = "[[非空]]";

  //获取列数
  const numCol = sheet.getDataRange().getNumColumns();
  //末尾列的标识符字母
  const endColId = String.fromCharCode(64+numCol);

  //辅助表会增加三行，第一行是”全部“，第二行是”空“，第三行是”非空“
  newHelperSheet.getRange(`A1:${endColId}3`).setValues([Array(numCol).fill(allVal), Array(numCol).fill(nullVal), Array(numCol).fill(notNullVal)]);

  //之后导入原表除表头之外的所有值
  const a4Helper = newHelperSheet.getRange("A4");
  a4Helper.setFormula(`=ARRAYFORMULA('${sheetName}'!A2:${endColId})`);

  const filterHeaderRanges = newFilterSheet.getRangeList(["A1", `A2:${endColId}2`]).getRanges();
  //在筛选表中导入原表表头
  filterHeaderRanges[0].setFormula(`=ARRAYFORMULA('${sheetName}'!A1:${endColId}1)`);
  //第二行为筛选行，默认筛选行的值全为”全部“
  filterHeaderRanges[1].setValues([Array(numCol).fill(allVal)])

  //为筛选行循环添加数据验证规则
  const filterValidCells = [];
  const helperColumns = [];
  for (let i = 1; i <= numCol; i++) {
    let curColId = String.fromCharCode(64+i);
    filterValidCells.push(`${curColId}2`);
    helperColumns.push(`'${newHelperSheetName}'!${curColId}:${curColId}`)
  }
  const filterValidCellsRanges = newFilterSheet.getRangeList(filterValidCells).getRanges();
  const helperColumnsRanges = newHelperSheet.getRangeList(helperColumns).getRanges();

  for (let i = 0; i < numCol; i++) {
    const rule = SpreadsheetApp.newDataValidation().requireValueInRange(helperColumnsRanges[i]).build();
    filterValidCellsRanges[i].setDataValidation(rule);
  }
  //调整冻结行
  newFilterSheet.setFrozenRows(2);

  //剩下的筛选表只有 A3 有一个复杂的公式，原表的表头越长，公式越长
  //但原理就是把每一列的值按照筛选行的值进行对比筛选，每一列都会”与“起来
  const a3 = newFilterSheet.getRange("A3");
  //原表每一列的范围，形如 [A2:A, B2:B, C2:C]
  let map_param = [];
  //lambda 的参数列表，形如 [xa, xb, xc]，目前最大支持 26 列
  let lambda_param = [];
  //lambda 的计算表达式，是一串 AND 链接起来的 IF 语句
  //初始值为 TRUE，方便后续用循环嵌套
  let lambda_expr = "TRUE";
  for (let i = 1; i <= numCol; i++) {
    //当前列的标识符字母
    let curColid = String.fromCharCode(64+i);
    map_param.push(`'${sheetName}'!${curColid}2:${curColid}`);
    let p = `x${curColid.toLowerCase()}`;
    lambda_param.push(p);
    //这里首先如果筛选值为”全部“，则直接返回 TRUE（所有行）
    //如果筛选值为”空“，就返回该列为空的行
    //如果筛选值为”非空“，就返回该列不是空的行
    //如果筛选值不是这些特殊值，就返回该列与之匹配的行
    //每一列的条件都与上一列”与“起来
    lambda_expr = `AND(IF(${curColid}2="${allVal}", TRUE, IF(${curColid}2="${nullVal}", ISBLANK(${p}), IF(${curColid}2="${notNullVal}", NOT(ISBLANK(${p})), ${p}=${curColid}2))), ${lambda_expr})`;
  }
  map_param = map_param.join(",");
  lambda_param = lambda_param.join(",");
  //筛选公式通过 MAP 和 LAMBDA 实现多列”与“，然后用 FILTER 过滤
  //这里不加 IFNA，因为加了之后日期格式的值就不会显示日期格式了，而只显示数字
  let a3_formula = `=FILTER('${sheetName}'!A2:${endColId}, MAP(${map_param}, LAMBDA(${lambda_param}, ${lambda_expr})))`;
  a3.setFormula(a3_formula);

  //隐藏辅助表
  newHelperSheet.hideSheet();
  //设置格式
  setAllRangeStyle(newFilterSheet);

  //增加条件格式，除了”全部“值之外，其他筛选值都会高亮显示，表示该列被筛选了
  const condRule = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(`=A2<>"${allVal}"`)
    .setBackground("#B7E1CD")
    .setRanges([filterHeaderRanges[1]])
    .build();
  let condRules = newFilterSheet.getConditionalFormatRules();
  condRules.push(condRule);
  newFilterSheet.setConditionalFormatRules(condRules);

  //保护工作表（没有必要，保护了调整列宽也限制）
}

function deleteFilterTable() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getActiveSheet();
  let sheetName = sheet.getName();

  let newHelperSheetName = `[${sheetName}]辅助`;
  let newFilterSheetName = `[${sheetName}]筛选`;
  //如果表格不存在会返回 null
  const oldHelperSheet = spreadsheet.getSheetByName(newHelperSheetName);
  const oldFilterSheet = spreadsheet.getSheetByName(newFilterSheetName);
  if (oldHelperSheet !== null) {
    spreadsheet.deleteSheet(oldHelperSheet);
  }
  if (oldFilterSheet !== null) {
    spreadsheet.deleteSheet(oldFilterSheet);
  }
}

function createSearchTable() {
  deleteSearchTable();

  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getActiveSheet();
  let sheetName = sheet.getName();

  let newSearchSheetName = `[${sheetName}]搜索`;
  const newSearchSheet = spreadsheet.insertSheet();
  newSearchSheet.setName(newSearchSheetName);

  //获取列数
  const numCol = sheet.getDataRange().getNumColumns();
  //末尾列的标识符字母
  const endColId = String.fromCharCode(64+numCol);

  const severalCellsRanges = newSearchSheet.getRangeList(["A1", "B1", "A2", "A3", "B2", "A4"]).getRanges();

  severalCellsRanges[0].setValue("搜索值");
  severalCellsRanges[1].setFormula(`=ARRAYFORMULA('${sheetName}'!A1:${endColId}1)`);
  // const a2 = newSearchSheet.getRange("A2");
  const validRule = SpreadsheetApp.newDataValidation().requireValueInRange(sheet.getRange(`A1:${endColId}1`)).build();
  severalCellsRanges[2].setDataValidation(validRule).setBackground("#4dd0e1");
  severalCellsRanges[3].setFormula(`=SUBSTITUTE(ADDRESS(1, MATCH(A2, '${sheetName}'!A1:${endColId}1, 0), 4), "1", "")`);
  severalCellsRanges[4].setFormula(`=FILTER('${sheetName}'!A2:${endColId}, ARRAYFORMULA(SEARCH(A4, INDIRECT("'${sheetName}'!"&A3&"2:"&A3), 1)))`);
  severalCellsRanges[5].setBackground("#b6d7a8")

  setAllRangeStyle(newSearchSheet);
  newSearchSheet.setFrozenRows(1);

  //保护工作表（没有必要，保护了调整列宽也限制）
}

function deleteSearchTable() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getActiveSheet();
  let sheetName = sheet.getName();

  let newSearchSheetName = `[${sheetName}]搜索`;
  const oldSearchSheet = spreadsheet.getSheetByName(newSearchSheetName);
  if (oldSearchSheet !== null) {
    spreadsheet.deleteSheet(oldSearchSheet);
  }
}

