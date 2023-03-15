///////////////////////////////////////////////////

/**
 * A 列作为 ID 列，自增
 */
function logAutoIncreaseId(edRow, edCol, sheet) {
  if (edCol === 1) return;

  const rangeList = sheet.getRangeList(["A2:A", `A${edRow}`]).getRanges();
  //当编辑行的自增列单元格为空时我们自增，如果已经有值我们忽略
  if (rangeList[1].getValue().length !== 0) return;

  //返回结果形如 [[1], [2], [""], ...]，需要降维
  const ids = rangeList[0].getValues().flat();
  //过滤掉非数字的值，包括空字符串
  const validIds = ids.filter(elem => typeof elem === "number");
  //找最大值并加一
  let nextId = validIds.reduce((a, b) => Math.max(a, b), 0) + 1;
  rangeList[1].setValue(nextId);
}

/**
 * C 列增加当前时间
 */
function logAutoAddDatetime(edRow, edCol, sheet) {
  if (edCol === 3) return;

  const cell = sheet.getRange(`C${edRow}`);
  if (cell.getValue().length !== 0) return;

  const ct = new Date();
  const timeString = `${ct.getFullYear()}-${ct.getMonth()+1}-${ct.getDate()} ${ct.getHours()}:${ct.getMinutes()}:${ct.getSeconds()}`;
  cell.setValue(timeString);
}

///////////////////////////////////////////////////

//key：表格名称
//value：该表格内需要自动执行的函数列表
let registeredAutoTasks = {
  "日志": [logAutoIncreaseId, logAutoAddDatetime, ],
};

///////////////////////////////////////////////////
/**
 * 该函数不用动
 */
function autoFill(e) {
  //如果是删除值，会返回 undefined，我们忽略删除值的情况
  if (e.value === undefined) return;
  const sheet = e.source.getActiveSheet();
  const sheetName = sheet.getName();
  //如果编辑的表格不在注册列表内
  if (!(sheetName in registeredAutoTasks)) return;
  let edCol = e.range.getColumn();
  let edRow = e.range.getRow();
  for (let func of registeredAutoTasks[sheetName]) {
    func(edRow, edCol, sheet);
  }
}

function onEdit(e) {
  autoFill(e);
}
